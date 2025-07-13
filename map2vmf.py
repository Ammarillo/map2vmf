import sys
import re
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QWidget, QPushButton, QTextEdit, QLabel, QFileDialog, 
                             QMessageBox, QProgressBar, QGroupBox, QLineEdit)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from PyQt5.QtGui import QFont, QIcon


class MapToVmfConverter:
    def __init__(self, default_texture="dev/dev_measuregeneric01b"):
        self.worldspawn_properties = {}
        self.brushes = []
        self.default_texture = default_texture
        
    def parse_map_file(self, map_content):
        """Parse .map file content and extract worldspawn and brushes"""
        lines = map_content.split('\n')
        in_worldspawn = False
        in_brush = False
        current_brush = None
        brace_depth = 0
        pending_brush = False
        brush_count = 0
        face_count = 0
        material_replacements = 0

        for line in lines:
            line = line.strip()

            # Detect start of brush (wait for '{' to actually start)
            if line.startswith('// brush'):
                pending_brush = True
                brush_count += 1
                continue

            # Worldspawn entity
            if line == '{' and not in_brush and not in_worldspawn and not pending_brush:
                in_worldspawn = True
                continue
            if in_worldspawn and line == '}' and not in_brush and not pending_brush:
                in_worldspawn = False
                continue

            # Parse worldspawn properties
            if in_worldspawn and line.startswith('"'):
                match = re.match(r'"([^"]+)"\s+"([^"]*)"', line)
                if match:
                    key, value = match.groups()
                    self.worldspawn_properties[key] = value
                continue

            # Start brush block only after '{' following '// brush'
            if pending_brush and line == '{':
                in_brush = True
                current_brush = {'faces': []}
                brace_depth = 1
                pending_brush = False
                continue

            # If pending_brush is set but line is not '{', just keep looking for '{'
            if pending_brush:
                continue

            # Brush block handling
            if in_brush:
                if line == '{':
                    brace_depth += 1
                    continue
                elif line == '}':
                    brace_depth -= 1
                    if brace_depth == 0:
                        # End of brush
                        in_brush = False
                        if current_brush:
                            self.brushes.append(current_brush)
                            current_brush = None
                    continue
                # Parse face lines
                if line.startswith('('):
                    face_match = re.match(r'\(\s*([^)]+)\s*\)\s*\(\s*([^)]+)\s*\)\s*\(\s*([^)]+)\s*\)\s+(\S+)\s+\[([^\]]+)\]\s+\[([^\]]+)\]\s+(\d+)\s+(\d+)\s+(\d+)', line)
                    if face_match:
                        p1, p2, p3, material, uaxis, vaxis, rotation, scale_x, scale_y = face_match.groups()
                        original_material = material
                        if material == "__TB_empty":
                            material = self.default_texture
                            material_replacements += 1
                        face = {
                            'p1': p1.strip(),
                            'p2': p2.strip(),
                            'p3': p3.strip(),
                            'material': material,
                            'uaxis': uaxis.strip(),
                            'vaxis': vaxis.strip(),
                            'rotation': int(rotation),
                            'scale_x': int(scale_x),
                            'scale_y': int(scale_y)
                        }
                        current_brush['faces'].append(face)
                        face_count += 1
                continue
        # No need to append at end; all brushes are appended on closing '}'
        
        # Return statistics for logging
        return {
            'brushes_found': brush_count,
            'brushes_processed': len(self.brushes),
            'faces_processed': face_count,
            'material_replacements': material_replacements
        }

    def generate_vmf(self):
        """Generate VMF content from parsed data"""
        vmf_lines = []
        
        # Worldspawn entity
        vmf_lines.append('world')
        vmf_lines.append('{')
        vmf_lines.append('\t"id" "0"')
        
        # Add worldspawn properties
        for key, value in self.worldspawn_properties.items():
            vmf_lines.append(f'\t"{key}" "{value}"')
        
        # Generate solids from brushes
        solid_id = 1
        side_id = 2
        
        for brush in self.brushes:
            vmf_lines.append('\tsolid')
            vmf_lines.append('\t{')
            vmf_lines.append(f'\t\t"id" "{solid_id}"')
            
            for face in brush['faces']:
                vmf_lines.append('\t\tside')
                vmf_lines.append('\t\t{')
                vmf_lines.append(f'\t\t\t"id" "{side_id}"')
                vmf_lines.append(f'\t\t\t"plane" "({face["p1"]}) ({face["p2"]}) ({face["p3"]})"')
                vmf_lines.append(f'\t\t\t"material" "{face["material"]}"')
                vmf_lines.append(f'\t\t\t"uaxis" "[{face["uaxis"]}] 0.25"')
                vmf_lines.append(f'\t\t\t"vaxis" "[{face["vaxis"]}] 0.25"')
                vmf_lines.append(f'\t\t\t"lightmapscale" "16"')
                vmf_lines.append('\t\t}')
                side_id += 1
            
            vmf_lines.append('\t}')
            solid_id += 1
        
        vmf_lines.append('}')
        
        return '\n'.join(vmf_lines)


class ConversionWorker(QThread):
    progress = pyqtSignal(int)
    finished = pyqtSignal(str)
    error = pyqtSignal(str)
    
    def __init__(self, input_file, output_file, default_texture):
        super().__init__()
        self.input_file = input_file
        self.output_file = output_file
        self.default_texture = default_texture
    
    def run(self):
        try:
            # Read input file
            with open(self.input_file, 'r', encoding='utf-8') as f:
                map_content = f.read()
            
            self.progress.emit(25)
            
            # Parse and convert
            converter = MapToVmfConverter(self.default_texture)
            stats = converter.parse_map_file(map_content)
            
            self.progress.emit(75)
            
            # Generate VMF content
            vmf_content = converter.generate_vmf()
            
            self.progress.emit(90)
            
            # Write output file
            with open(self.output_file, 'w', encoding='utf-8') as f:
                f.write(vmf_content)
            
            self.progress.emit(100)
            
            # Create detailed success message
            message = f"Successfully converted {self.input_file} to {self.output_file}\n\n"
            message += f"Conversion Statistics:\n"
            message += f"• Brushes found: {stats['brushes_found']}\n"
            message += f"• Brushes processed: {stats['brushes_processed']}\n"
            message += f"• Faces processed: {stats['faces_processed']}\n"
            message += f"• Material replacements: {stats['material_replacements']}\n"
            message += f"• Default texture used: {self.default_texture}\n"
            message += f"• Output file size: {len(vmf_content)} characters"
            
            self.finished.emit(message)
            
        except Exception as e:
            self.error.emit(f"Error during conversion: {str(e)}")


class MapToVmfConverterGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Map to VMF Converter")
        self.setGeometry(100, 100, 600, 500)
        
        # Create central widget and layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Title
        title_label = QLabel("Map to VMF Converter")
        title_label.setFont(QFont("Arial", 16, QFont.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)
        
        # File selection group
        file_group = QGroupBox("File Selection")
        file_layout = QVBoxLayout(file_group)
        
        # Input file selection
        input_layout = QHBoxLayout()
        self.input_label = QLabel("No input file selected")
        input_btn = QPushButton("Select .map File")
        input_btn.clicked.connect(self.select_input_file)
        input_layout.addWidget(QLabel("Input File:"))
        input_layout.addWidget(self.input_label)
        input_layout.addWidget(input_btn)
        file_layout.addLayout(input_layout)
        
        # Output file selection
        output_layout = QHBoxLayout()
        self.output_label = QLabel("No output file selected")
        output_btn = QPushButton("Select Output Location")
        output_btn.clicked.connect(self.select_output_file)
        output_layout.addWidget(QLabel("Output File:"))
        output_layout.addWidget(self.output_label)
        output_layout.addWidget(output_btn)
        file_layout.addLayout(output_layout)
        
        layout.addWidget(file_group)
        
        # Texture settings group
        texture_group = QGroupBox("Texture Settings")
        texture_layout = QVBoxLayout(texture_group)
        
        # Default texture input
        texture_input_layout = QHBoxLayout()
        texture_input_layout.addWidget(QLabel("Default Texture Path:"))
        self.texture_input = QLineEdit()
        self.texture_input.setText("dev/dev_measuregeneric01b")
        self.texture_input.setPlaceholderText("Enter texture path (e.g., dev/dev_measuregeneric01b)")
        texture_input_layout.addWidget(self.texture_input)
        texture_layout.addLayout(texture_input_layout)
        
        # Add help text
        help_label = QLabel("This texture will be used to replace '__TB_empty' materials in the map file.")
        help_label.setStyleSheet("color: gray; font-size: 10px;")
        texture_layout.addWidget(help_label)
        
        layout.addWidget(texture_group)
        
        # Conversion controls
        convert_group = QGroupBox("Conversion")
        convert_layout = QVBoxLayout(convert_group)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        convert_layout.addWidget(self.progress_bar)
        
        # Convert button
        self.convert_btn = QPushButton("Convert Map to VMF")
        self.convert_btn.clicked.connect(self.start_conversion)
        self.convert_btn.setEnabled(False)
        convert_layout.addWidget(self.convert_btn)
        
        layout.addWidget(convert_group)
        
        # Log area
        log_group = QGroupBox("Conversion Log")
        log_layout = QVBoxLayout(log_group)
        
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setMaximumHeight(200)
        log_layout.addWidget(self.log_text)
        
        layout.addWidget(log_group)
        
        # Status bar
        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")
        
        # Initialize variables
        self.input_file = None
        self.output_file = None
        self.worker = None
    
    def select_input_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Select .map File", "", "Map Files (*.map);;All Files (*)"
        )
        if file_path:
            self.input_file = file_path
            self.input_label.setText(file_path)
            self.check_ready()
    
    def select_output_file(self):
        file_path, _ = QFileDialog.getSaveFileName(
            self, "Save VMF File", "", "VMF Files (*.vmf);;All Files (*)"
        )
        if file_path:
            self.output_file = file_path
            self.output_label.setText(file_path)
            self.check_ready()
    
    def check_ready(self):
        self.convert_btn.setEnabled(bool(self.input_file and self.output_file))
    
    def start_conversion(self):
        if not self.input_file or not self.output_file:
            QMessageBox.warning(self, "Error", "Please select both input and output files.")
            return
        
        # Get the custom texture path
        default_texture = self.texture_input.text().strip()
        if not default_texture:
            default_texture = "dev/dev_measuregeneric01b"
        
        # Disable UI during conversion
        self.convert_btn.setEnabled(False)
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        # Clear log and add initial message
        self.log_text.clear()
        self.log_text.append("=== Map to VMF Conversion Started ===")
        self.log_text.append(f"Input file: {self.input_file}")
        self.log_text.append(f"Output file: {self.output_file}")
        self.log_text.append(f"Default texture: {default_texture}")
        self.log_text.append("")
        
        # Start conversion in background thread
        self.worker = ConversionWorker(self.input_file, self.output_file, default_texture)
        self.worker.progress.connect(self.progress_bar.setValue)
        self.worker.finished.connect(self.conversion_finished)
        self.worker.error.connect(self.conversion_error)
        self.worker.start()
        
        self.log_text.append("Starting conversion...")
        self.status_bar.showMessage("Converting...")
    
    def conversion_finished(self, message):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Add detailed log information
        self.log_text.append("=== Conversion Completed Successfully ===")
        self.log_text.append(message)
        self.log_text.append("")
        self.log_text.append("=== End of Conversion ===")
        
        self.status_bar.showMessage("Conversion completed")
        QMessageBox.information(self, "Success", "Conversion completed successfully!")
    
    def conversion_error(self, error_message):
        self.convert_btn.setEnabled(True)
        self.progress_bar.setVisible(False)
        
        # Add error information to log
        self.log_text.append("=== Conversion Failed ===")
        self.log_text.append(f"Error: {error_message}")
        self.log_text.append("")
        self.log_text.append("=== End of Conversion ===")
        
        self.status_bar.showMessage("Conversion failed")
        QMessageBox.critical(self, "Error", error_message)


def main():
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    
    window = MapToVmfConverterGUI()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
