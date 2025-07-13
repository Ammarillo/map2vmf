# Map to VMF Converter

A Python GUI application that converts Source Engine `.map` files to Valve Map Format (`.vmf`) files. This tool is designed to help map creators convert their map files for use in Source Engine games like Half-Life 2, Counter-Strike, and other Source-based games.

## Features

- **Graphical User Interface**: Easy-to-use PyQt5-based GUI
- **Custom Texture Support**: Specify custom texture paths for material replacement
- **Progress Tracking**: Real-time conversion progress with detailed logging
- **Material Replacement**: Automatically replaces `__TB_empty` materials with a user-defined texture
- **Detailed Statistics**: Shows conversion statistics including brush count, face count, and material replacements
- **Cross-Platform**: Works on Windows, macOS, and Linux
- **Standalone Executable**: Can be built into a self-contained executable that doesn't require Python installation

## Requirements

- Python 3.6 or higher
- PyQt5 5.15.0 or higher

## Installation

### Option 1: Run from Source

1. **Clone or download the project files**
   ```bash
   git clone https://github.com/Ammarillo/map2vmf.git
   cd map2vmf
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run the application**
   ```bash
   python map2vmf.py
   ```

### Option 2: Build Standalone Executable

1. **Clone or download the project files**
   ```bash
   git clone https://github.com/Ammarillo/map2vmf.git
   cd map2vmf
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Build the executable**
   ```bash
   python build_exe.py
   ```

4. **Run the executable**
   - **Windows**: Double-click `dist/Map2VMF_Converter.exe`
   - **Linux/Mac**: Run `./dist/Map2VMF_Converter`

## Usage

### Running the Application

#### From Source Code
1. **Start the application**
   ```bash
   python map2vmf.py
   ```

#### From Executable
1. **Run the standalone executable**
   - **Windows**: Double-click `Map2VMF_Converter.exe`
   - **Linux/Mac**: Run `./Map2VMF_Converter`

2. **Select Input File**
   - Click "Select .map File" to choose your Source Engine `.map` file
   - The application supports standard Source Engine map files

3. **Configure Texture Settings** (Optional)
   - The default texture path is `dev/dev_measuregeneric01b`
   - You can change this to any texture path you prefer
   - This texture will replace all `__TB_empty` materials in the map

4. **Select Output Location**
   - Click "Select Output Location" to choose where to save the `.vmf` file
   - The output file will be in Valve Map Format

5. **Convert**
   - Click "Convert Map to VMF" to start the conversion process
   - Monitor the progress bar and conversion log for real-time updates

### Understanding the Output

The conversion process will show detailed statistics including:
- Number of brushes found and processed
- Number of faces processed
- Number of material replacements made
- Default texture used
- Output file size

## File Formats

### Input: .map Files
Source Engine map files contain:
- Worldspawn entity with properties
- Brush definitions with faces
- Material assignments
- Texture coordinates and scaling

### Output: .vmf Files
Valve Map Format files contain:
- Worldspawn entity with preserved properties
- Solids (converted from brushes)
- Sides (converted from faces)
- Material assignments
- Texture coordinates and scaling

## Material Replacement

The converter automatically replaces `__TB_empty` materials with a user-defined texture. This is useful for:
- Converting placeholder materials to actual textures
- Ensuring compatibility with Source Engine games
- Maintaining visual consistency in converted maps

## Troubleshooting

### Common Issues

1. **"No input file selected"**
   - Make sure you've selected a valid `.map` file
   - Check that the file exists and is readable

2. **"No output file selected"**
   - Ensure you've chosen a location to save the `.vmf` file
   - Make sure you have write permissions in the target directory

3. **Conversion errors**
   - Check that the input file is a valid Source Engine map file
   - Verify the file isn't corrupted or incomplete
   - Review the conversion log for specific error messages

4. **PyQt5 installation issues**
   - On some systems, you may need to install additional dependencies:
     ```bash
     # Ubuntu/Debian
     sudo apt-get install python3-pyqt5
     
     # macOS (with Homebrew)
     brew install pyqt5
     ```

### Getting Help

If you encounter issues:
1. Check the conversion log for detailed error messages
2. Verify your input file is a valid Source Engine map file
3. Ensure all dependencies are properly installed
4. Check file permissions for input and output locations

## Technical Details

### Architecture
- **MapToVmfConverter**: Core conversion logic
- **ConversionWorker**: Background processing thread
- **MapToVmfConverterGUI**: PyQt5-based user interface

### Conversion Process
1. Parse `.map` file content
2. Extract worldspawn properties
3. Process brush definitions
4. Convert faces to sides
5. Apply material replacements
6. Generate VMF format output

### Supported Features
- Worldspawn entity properties
- Brush geometry and faces
- Material assignments
- Texture coordinates (uaxis/vaxis)
- Texture scaling
- Lightmap scaling

## License

This project is open source. Feel free to modify and distribute according to your needs.

## Contributing

Contributions are welcome! Please feel free to submit issues, feature requests, or pull requests.

## Version History

- **v1.0**: Initial release with basic conversion functionality
- **v1.1**: Added custom texture path support
- **v1.2**: Enhanced GUI with progress tracking and detailed logging 