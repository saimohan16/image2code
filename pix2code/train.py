import argparse
import torch
import math
import os
from pathlib import Path
from vocab import Vocab
from torch.utils.data import DataLoader
from dataset import Pix2CodeDataset
from utils import collate_fn, save_model, resnet_img_transformation
from models import Encoder, Decoder
import torch.multiprocessing as mp

# Fix multiprocessing issues on Windows
if __name__ == '__main__':
    mp.set_start_method('spawn', force=True)

    # Fix OpenMP conflict issues
    os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

    # Argument parser
    parser = argparse.ArgumentParser(description='Train the model')

    parser.add_argument("--data_path", type=str, default="data/web/all_data", help="Path to the dataset")
    parser.add_argument("--vocab_file_path", type=str, default=None, help="Path to the vocab file")
    parser.add_argument("--cuda", action='store_true', default=True, help="Use CUDA if available")
    parser.add_argument("--img_crop_size", type=int, default=224)
    parser.add_argument("--split", type=str, default="train")
    parser.add_argument("--save_after_epochs", type=int, default=1, help="Save model checkpoint every n epochs")
    parser.add_argument("--models_dir", type=str, default="models", help="Directory to save trained models")
    parser.add_argument("--batch_size", type=int, default=4)
    parser.add_argument("--epochs", type=int, default=15)
    parser.add_argument("--lr", type=float, default=1e-3, help="Learning rate")
    parser.add_argument("--print_freq", type=int, default=1, help="Print training stats every n epochs")
    parser.add_argument("--seed", type=int, default=2020, help="Random seed for reproducibility")

    args = parser.parse_args()
    args.vocab_file_path = args.vocab_file_path or Path(args.data_path).parent / "vocab.txt"

    print("Training args:", args)

    # Set seeds for reproducibility
    torch.manual_seed(args.seed)
    torch.cuda.manual_seed(args.seed)

    # Load vocabulary
    vocab = Vocab(args.vocab_file_path)
    assert len(vocab) > 0, "Vocabulary is empty!"

    # Setup GPU/CPU
    use_cuda = args.cuda and torch.cuda.is_available()
    device = torch.device("cuda" if use_cuda else "cpu")

    if use_cuda:
        print(f"Using GPU: {torch.cuda.get_device_name(0)}")
    else:
        print("CUDA not available, training on CPU.")

    # Data transformations
    transform_imgs = resnet_img_transformation(args.img_crop_size)

    # Adjust num_workers based on OS
    num_workers = 4 if use_cuda and os.name != 'nt' else 0

    # Creating the DataLoader
    train_loader = DataLoader(
        Pix2CodeDataset(args.data_path, args.split, vocab, transform=transform_imgs),
        batch_size=args.batch_size,
        collate_fn=lambda data: collate_fn(data, vocab=vocab),
        pin_memory=use_cuda,
        num_workers=num_workers,
        drop_last=True
    )
    print("DataLoader initialized.")

    # Define model parameters
    embed_size = 256
    hidden_size = 512
    num_layers = 1
    lr = args.lr

    # Initialize models
    encoder = Encoder(embed_size).to(device)
    decoder = Decoder(embed_size, hidden_size, len(vocab), num_layers).to(device)

    # Define optimizer and loss function
    criterion = torch.nn.CrossEntropyLoss()
    params = list(decoder.parameters()) + list(encoder.linear.parameters()) + list(encoder.BatchNorm.parameters())
    optimizer = torch.optim.Adam(params, lr=lr)

    # Training loop
    print("Starting Training...")
    for epoch in range(args.epochs):
        for i, (images, captions, lengths) in enumerate(train_loader):
            images, captions = images.to(device), captions.to(device)

            targets = torch.nn.utils.rnn.pack_padded_sequence(input=captions, lengths=lengths, batch_first=True)[0]

            encoder.zero_grad()
            decoder.zero_grad()

            features = encoder(images)
            output = decoder(features, captions, lengths)
            loss = criterion(output, targets)

            loss.backward()
            optimizer.step()

            if epoch % args.print_freq == 0 and i == 0:
                print(f"Epoch {epoch} | Loss: {loss.item():.4f} | Perplexity: {math.exp(loss.item()):.4f}")

        # Save model checkpoint
        if epoch != 0 and epoch % args.save_after_epochs == 0:
            save_model(args.models_dir, encoder, decoder, optimizer, epoch, loss.item(), args.batch_size, vocab)
            print(f"Checkpoint saved at epoch {epoch}")

    # Save final model
    print("Training Complete!")
    save_model(args.models_dir, encoder, decoder, optimizer, args.epochs, loss.item(), args.batch_size, vocab)
    print("Final model saved.")
