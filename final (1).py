import os
import cv2
import numpy as np
from PIL import Image as PilImage
from io import BytesIO
from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.image import Image as KivyImage
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.textinput import TextInput
from kivy.core.image import Image as CoreImage
from kivy.graphics import Color, Rectangle
from kivy.clock import Clock

class ImageSketchConverter:
    @staticmethod
    def convert_to_sketch(image_path):
        try:
            # Read the image
            original_image = cv2.imread(image_path)

            # Convert the image to grayscale
            gray_image = cv2.cvtColor(original_image, cv2.COLOR_BGR2GRAY)

            # Invert the image
            inverted_image = cv2.bitwise_not(gray_image)

            # Apply GaussianBlur to the inverted image
            blurred_image = cv2.GaussianBlur(inverted_image, (111, 111), 0)

            # Invert the blurred image
            inverted_blurred_image = cv2.bitwise_not(blurred_image)

            # Sketch is the combination of the grayscale image and the inverted and blurred image
            sketch = cv2.divide(gray_image, inverted_blurred_image, scale=256.0)

            # Convert the NumPy array to a PIL Image
            pil_image = PilImage.fromarray(sketch)

            # Save the PIL Image to a BytesIO buffer
            buffer = BytesIO()
            pil_image.save(buffer, format="PNG")

            # Reset the buffer position to the beginning
            buffer.seek(0)

            # Return the BytesIO buffer
            return buffer
        except Exception as e:
            print(f"Error converting image to sketch: {e}")
            return None

class ImageSketchApp(App):
    def build(self):
        self.icon = "logo1.png"
        self.image_converter = ImageSketchConverter()

        # Create the main layout
        main_layout = BoxLayout(orientation='horizontal', spacing=10, padding=(10, 10))

        # Create a vertical layout for the left side
        left_layout = BoxLayout(orientation='vertical', spacing=10)

        # Add a colored background to the left side
        with left_layout.canvas.before:
            Color(0.2, 0.2, 0.2, 1)  # Dark Gray
            Rectangle(pos=left_layout.pos, size=(600, 600))  # Adjust size as needed

        # Create the image display on the left side
        self.image_display = KivyImage(size=(600, 600))
        left_layout.add_widget(self.image_display)

        main_layout.add_widget(left_layout)

        # Create a vertical layout for the right side
        right_layout = BoxLayout(orientation='vertical', spacing=10)

        # Create the file chooser
        self.file_chooser = FileChooserListView()
        self.file_chooser.bind(selection=self.on_file_selected)
        right_layout.add_widget(self.file_chooser)

        # Create the convert button
        convert_button = Button(text="Convert to Sketch", size_hint_y=None, height=50,background_color=(0.5, 0.7, 0.3, 1))  # Light Green
        convert_button.bind(on_release=self.convert_to_sketch)
        right_layout.add_widget(convert_button)

        # Create a text input for output name
        self.output_name_input = TextInput(multiline=False, hint_text='Output Name', size_hint=(1, 0.1))
        right_layout.add_widget(self.output_name_input)

        # Create a text input for file type
        self.file_type_input = TextInput(multiline=False, hint_text='File Type (e.g., png)', size_hint=(1, 0.1))
        right_layout.add_widget(self.file_type_input)

        # Create the download button
        download_button = Button(text="Download Sketch", size_hint_y=None, height=50, background_color=(0.5, 0.5, 0.8, 1))  # Light Blue
        download_button.bind(on_release=self.download_sketch)
        right_layout.add_widget(download_button)

        main_layout.add_widget(right_layout)

        return main_layout

    def on_file_selected(self, instance, value):
        """Called when a file is selected in the file chooser."""
        if value:
            image_path = value[0]
            self.load_image(image_path)

    def load_image(self, image_path):
        """Load and display the selected image."""
        try:
            # Load the original image
            original_buffer = BytesIO(open(image_path, "rb").read())
            original_image = CoreImage(original_buffer, ext='png')
            self.image_display.texture = original_image.texture
        except Exception as e:
            print(f"Error loading image: {e}")

    def convert_to_sketch(self, instance):
        """Convert the selected image to a sketch."""
        try:
            if self.file_chooser.selection:
                image_path = self.file_chooser.selection[0]
                # Load the original image first
                self.load_image(image_path)
                # Convert the loaded image to a sketch after a short delay
                Clock.schedule_once(lambda dt: self.perform_conversion(image_path), 0.5)
            else:
                print("Error: No file selected")
        except Exception as e:
            print(f"Error converting image to sketch: {e}")

    def perform_conversion(self, image_path):
        """Perform the conversion of the selected image to a sketch."""
        try:
            sketch_buffer = self.image_converter.convert_to_sketch(image_path)
            if sketch_buffer:
                # Load the sketch image using CoreImage
                sketch_image = CoreImage(BytesIO(sketch_buffer.getvalue()), ext='png')
                self.image_display.texture = sketch_image.texture
        except Exception as e:
            print(f"Error converting image to sketch: {e}")

    def download_sketch(self, instance):
        """Download the converted sketch."""
        try:
            if self.file_chooser.selection:
                original_image_path = self.file_chooser.selection[0]
                sketch_buffer = self.image_converter.convert_to_sketch(original_image_path)

                if sketch_buffer:
                    # Get the directory of the original image
                    output_directory = os.path.dirname(original_image_path)

                    # Get output name from the input field or use a default name
                    output_name = self.output_name_input.text.strip()
                    if not output_name:
                        output_name = "sketch_output"

                    # Get file type from the input field or use a default type
                    file_type = self.file_type_input.text.strip()
                    if not file_type:
                        file_type = "png"

                    # Generate a filename for the sketch
                    sketch_filename = os.path.join(output_directory, f"{output_name}.{file_type}")

                    # Save the sketched image
                    with open(sketch_filename, "wb") as sketch_file:
                        sketch_file.write(sketch_buffer.getvalue())

                    print(f"Sketch saved at: {sketch_filename}")
                else:
                    print("Error: Could not create sketch")
            else:
                print("Error: No file selected")
        except Exception as e:
            print(f"Error downloading sketch: {e}")

if __name__ == '__main__':
    ImageSketchApp().run()
