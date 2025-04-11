from zss import simple_distance, Node, distance
from bs4 import BeautifulSoup
import re

def count_nodes(node):
    """
    Recursively count the number of nodes in a tree.

    Parameters:
    node (Node): The root node of the tree.

    Returns:
    int: The number of nodes in the tree.
    """
    if not node:
        return 0
    
    count = 1  # count the current node

    # recursively count the nodes in the children
    for child in Node.get_children(node):
        count += count_nodes(child)
    
    return count

def create_tree(html):
    """
    Creates a tree structure from a given HTML document.

    Parameters:
    html (str): The HTML document in string format.

    Returns:
    Node: The root node of the created tree.
    """
    soup = BeautifulSoup(html, 'html.parser')
    root = Node(soup.name if soup.name else 'root')
    create_tree_recursive(soup, root)
    number_nodes = count_nodes(root)
    return root, number_nodes

def create_tree_recursive(bs4node, zssnode):
    """
    Recursively adds child nodes to a given root node, effectively building a tree structure.

    Parameters:
    bs4node (BeautifulSoup element): The current BeautifulSoup element being processed.
    zssnode (Node): The current tree node to which child nodes will be added.
    """
    for child in bs4node.children:
        if child.name:  # this will ignore text nodes
            newnode = Node(child.name)
            zssnode.addkid(newnode)
            create_tree_recursive(child, newnode)

def calculate_ted(html1, html2):
    """
    Calculates the Tree Edit Distance (TED) between two HTML documents.
    All operations cost 1 (insert, remove, update)

    Parameters:
    html1, html2 (str): The HTML documents to be compared.

    Returns:
    float: The Tree Edit Distance between the two HTML documents. 
    float: The Normalized Tree Edit Distance between the two HTML documents, divided by the bigger number of nodes. 
    """
    tree1, nodes1 = create_tree(html1)
    tree2, nodes2 = create_tree(html2)
    #return simple_distance(tree1, tree2)
    d = distance(
        tree1, tree2, Node.get_children,
        insert_cost=lambda _: 1,
        remove_cost=lambda _: 1,
        update_cost=lambda a, b: 0 if Node.get_label(a) == Node.get_label(b) else 1,
        return_operations=False)
    
    return d, d / (max(nodes1, nodes2))

def extract_html_tree(html):
    """
    Extracts the HTML tree enclosed between <html> and </html> tags from a string.
    If one of the tags or both of the tags are not present, return an empty tree.

    Parameters:
    html (str): The string from which to extract the HTML tree.

    Returns:
    str: The extracted HTML tree. If no <html> and/or </html> tags are found, returns an empty HTML tree.
    """
    match = re.search(r'(<html>.*?</html>)', html, re.DOTALL)
    if match:
        return match.group()
    else:
        # <html> and/or </html> tags not found, return empty html tree 
        return '<html> </html>' 

def calculate_ted_from_file_paths(file_path_1, file_path_2):
    """
    Calculates the Tree Edit Distance (TED) between two HTML documents, given their file paths.

    Parameters:
    file_path_1, file_path_2 (str): The file paths to the HTML documents to be compared.

    Returns:
    float: The Tree Edit Distance between the two HTML documents.
    """
    with open(file_path_1, 'r') as f1:
        html_1 = extract_html_tree(f1.read())

    with open(file_path_2, 'r') as f2:
        html_2 = extract_html_tree(f2.read())
    return calculate_ted(html_1, html_2)

if __name__ == '__main__':
    file_name_1 = 'examples/rw_8.html'
    file_name_2 = 'examples/rw_9.html'

    ted, n_ted = calculate_ted_from_file_paths(file_name_1, file_name_2)
    print(f'Html Tree Edit Distance:            {ted:.2f}')
    print(f'Normalized Html Tree Edit Distance: {n_ted:.2f}')
