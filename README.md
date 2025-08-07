# Minimal AI Launcher

A lightweight, floating AI assistant launcher for Linux desktop environments. Get instant access to Google's Gemini AI through a sleek, overlay interface that appears on demand and disappears when you're done.

![AI Launcher Demo](demo.gif)

## Features

- **Floating Overlay Interface**: Always-on-top, translucent window that appears in the center of your screen
- **Instant AI Access**: Direct integration with Google Gemini 2.5 Flash for fast responses
- **Smart Resizing**: Window automatically adjusts height based on conversation length
- **Streamlined UX**: Auto-closes on focus loss, start new conversations by simply typing
- **Built-in Commands**: Quick shortcuts for common applications
- **Minimal Resource Usage**: Lightweight GTK3 application with low memory footprint

## Quick Commands

- `/b` - Open web browser
- `/f` - Open file manager (Thunar)
- `/t` - Open terminal (xfce4-terminal)
- `Escape` - Close the launcher

## Installation

### Prerequisites

- Linux desktop environment with compositing support
- Python 3.6+
- GTK 3.0
- Google Gemini API key

### Automatic Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/minimal-ai-launcher.git
cd minimal-ai-launcher
```

2. Run the installation script:
```bash
chmod +x install.sh
./install.sh
```

3. Edit the `.env` file and add your Gemini API key:
```bash
nano .env
```

### Manual Installation

1. Install system dependencies:
```bash
sudo apt-get update
sudo apt-get install -y python3-gi python3-gi-cairo gir1.2-gtk-3.0
```

2. Create virtual environment:
```bash
python3 -m venv venv --system-site-packages
source venv/bin/activate
```

3. Install Python dependencies:
```bash
pip install google-generativeai python-dotenv
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env file with your Gemini API key
```

## Usage

1. Activate the virtual environment:
```bash
source venv/bin/activate
```

2. Launch the AI assistant:
```bash
python3 main.py
```

3. The floating window will appear in the center of your screen. Start typing your question or command.

4. Press `Enter` to send your message to the AI.

5. The window will automatically close when it loses focus, or press `Escape` to close manually.

6. To start a new conversation, simply start typing when the previous response is complete.

## Configuration

Edit the `Config` class in `main.py` to customize:

- **Window dimensions**: `INITIAL_WIDTH`, `INITIAL_HEIGHT`, `MAX_HEIGHT`
- **Appearance**: `FONT_FAMILY`, `FONT_SIZE`, `PADDING`
- **AI model**: `GEMINI_MODEL` (default: gemini-2.5-flash)

## API Key Setup

1. Visit [Google AI Studio](https://makersuite.google.com/app/apikey)
2. Create a new API key for Gemini
3. Add the key to your `.env` file:
```
GEMINI_API_KEY=your_actual_api_key_here
```

## Keyboard Shortcuts

- **Enter**: Send message to AI
- **Shift+Enter**: Add line break
- **Escape**: Close application
- **Arrow Keys**: Scroll through long responses (when scrollbar is visible)

## System Integration

For quick access, consider:

1. **Creating a desktop shortcut**
2. **Setting up a global hotkey** using your desktop environment's keyboard settings
3. **Adding to startup applications** for always-available access

## Requirements

- **Python**: 3.6 or higher
- **System packages**: python3-gi, python3-gi-cairo, gir1.2-gtk-3.0
- **Python packages**: google-generativeai, python-dotenv
- **Desktop**: Compositing window manager for transparency effects

## Troubleshooting

### Common Issues

**"GEMINI_API_KEY not found" error**
- Ensure your `.env` file exists and contains `GEMINI_API_KEY=your_key_here`
- Verify the API key is valid at Google AI Studio

**Window doesn't appear transparent**
- Enable desktop composition in your window manager
- Try running with different visual themes

**GTK warnings or crashes**
- Ensure all GTK3 dependencies are installed
- Check that python3-gi is properly installed with system site packages

**API rate limits**
- Gemini has usage quotas; check your API usage in Google AI Studio
- Consider upgrading your API tier for higher limits

### Debug Mode

Run with debug output:
```bash
python3 main.py 2>&1 | tee debug.log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Test thoroughly on your system
5. Submit a pull request

## License

MIT License - see LICENSE file for details.

## Acknowledgments

- Built with [Google Gemini API](https://ai.google.dev/)
- Uses [GTK 3](https://gtk.org/) for the user interface
- Inspired by launcher applications like Alfred and Raycast