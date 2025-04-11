import sass
import os


class ColorManager:
    def compile_color(primary=None, secondary=None, light=None, dark=None, enable_gradients=True, output_path="./output/", assets_path=""):

        sass_vars = {
            "$body-bg": "#FFF",
            "$primary": primary,
            "$secondary": secondary,
            "$light": light,
            "$dark": dark,
            "$enable-gradients": "true" if enable_gradients else "false"
        }

        scss = ""
        for var in sass_vars:
            scss = scss + var+":"+sass_vars[var]+"; \n"
        scss += f'@import "{assets_path}/vendor/bootstrap-dist-4.3.1/scss/bootstrap";'

        with open(output_path+'custom-bootstrap.scss', 'w') as example_scss:
            example_scss.write(scss)
        sass.compile(dirname=(output_path, output_path+'css'),
                     output_style='compressed')
        os.remove(output_path+'custom-bootstrap.scss')
