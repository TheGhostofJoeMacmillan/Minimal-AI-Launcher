
import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import requests
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Configure the Groq API ---
api_key = os.getenv("GROQ_API_KEY")
if not api_key:
    print("Error: GROQ_API_KEY not found in .env file. Please create a .env file and add your key.", file=sys.stderr)
    exit(1)

GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"  # Example endpoint

class AiLauncher(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="AI Launcher")
        self.set_decorated(False)
        self.set_keep_above(True)
        
        # --- State and Sizing ---
        self.initial_size = (600, 50)
        self.max_height = 400 # Set max height to 400px
        self.set_default_size(self.initial_size[0], self.initial_size[1])
        self.conversation_complete = False

        # --- Event Handlers ---
        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_window_key_press)

        # --- UI Elements ---
        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.connect("key-press-event", self.on_textview_key_press)
        self.buffer = self.textview.get_buffer()
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        # Connect to the size-allocate signal for reliable scroll checking
        self.scrolled_window.connect("size-allocate", self.on_size_allocated)
        self.scrolled_window.add(self.textview)
        self.add(self.scrolled_window)

        # --- Final Setup ---
        self.load_css()
        self.create_tags()
        self.position_in_center()
        self.show_all()
        self.textview.grab_focus()
        self.insert_prompt()

    def position_in_center(self):
        display = self.get_display()
        monitor = display.get_primary_monitor()
        self.messages = []  # Store conversation history
        if not monitor: monitor = display.get_monitor(0)
        workarea = monitor.get_geometry()
        win_width, win_height = self.get_size()
        x = workarea.x + (workarea.width - win_width) // 2
        y = workarea.y + (workarea.height - win_height) // 2
        self.move(x, y)

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = b'''
        window { background-color: black; }
        textview, text {
            background-color: black;
            color: white;
            font-family: monospace;
            font-size: 14pt;
        }
        scrolledwindow { background-color: black; }
        textview { padding: 5px; }
        '''
        css_provider.load_from_data(css)
        context = self.get_style_context()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_tags(self):
        self.buffer.create_tag("user_tag", foreground="#ffffff")
        self.buffer.create_tag("ai_tag", foreground="#ffffff")
        self.buffer.create_tag("prompt_tag", foreground="#ffffff")
        self.buffer.create_tag("uneditable", editable=False)

    def insert_prompt(self):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(end_iter, "> ", "prompt_tag")
        self.input_start_offset = self.buffer.get_char_count()
        self.buffer.apply_tag_by_name("uneditable", self.buffer.get_start_iter(), self.buffer.get_iter_at_offset(self.input_start_offset))

    def on_window_key_press(self, widget, event):
        if event.keyval == Gdk.KEY_Escape:
            Gtk.main_quit()
            return True
        return False

    def on_textview_key_press(self, widget, event):
        if self.scrolled_window.get_policy()[1] == Gtk.PolicyType.AUTOMATIC:
            adj = self.scrolled_window.get_vadjustment()
            step = adj.get_step_increment()
            if event.keyval == Gdk.KEY_Up:
                adj.set_value(adj.get_value() - step)
                return True
            elif event.keyval == Gdk.KEY_Down:
                adj.set_value(adj.get_value() + step)
                return True

        if self.conversation_complete and event.string and event.string.isprintable():
            self.reset_for_new_query(event.string)
            return True

        if event.keyval == Gdk.KEY_Return and not event.state & Gdk.ModifierType.SHIFT_MASK:
            start_iter = self.buffer.get_iter_at_offset(self.input_start_offset)
            end_iter = self.buffer.get_end_iter()
            user_text = self.buffer.get_text(start_iter, end_iter, True).strip()

            if user_text:
                self.conversation_complete = False
                self.buffer.apply_tag_by_name("user_tag", start_iter, end_iter)
                GLib.idle_add(self.get_ai_response, user_text)
            return True
        
        return False

    def reset_for_new_query(self, initial_char):
        self.buffer.set_text("")
        self.resize(self.initial_size[0], self.initial_size[1])
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.insert_prompt()
        self.buffer.insert(self.buffer.get_end_iter(), initial_char)
        self.conversation_complete = False

    def get_ai_response(self, user_text):
        try:
            headers = {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.3-70b-versatile",
                "messages": [
                    {"role": "user", "content": user_text}
                ]
            }
            response = requests.post(GROQ_API_URL, headers=headers, json=data)
            response.raise_for_status()
            ai_message = response.json()["choices"][0]["message"]["content"]
            self.append_message(ai_message)
        except Exception as e:
            self.append_message(f"Error: {e}")
        finally:
            self.insert_prompt()
            self.resize_window()
            self.conversation_complete = True
        return False

    def append_message(self, message):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert(end_iter, f"\n\n{message}")

    def resize_window(self):
        line_count = self.buffer.get_line_count()
        desired_height = line_count * 28
        
        new_height = min(desired_height, self.max_height)
        new_height = max(self.initial_size[1], new_height)

        self.resize(self.initial_size[0], new_height)

    def on_size_allocated(self, widget, allocation):
        """Called whenever the scrolled_window is resized."""
        vadjustment = self.scrolled_window.get_vadjustment()
        if vadjustment.get_upper() > vadjustment.get_page_size():
            self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.AUTOMATIC)
        else:
            self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

    def on_focus_out(self, widget, event):
        Gtk.main_quit()

# --- Main Execution ---
if __name__ == "__main__":
    win = AiLauncher()
    screen = win.get_screen()
    visual = screen.get_rgba_visual()
    if visual and screen.is_composited():
        win.set_visual(visual)
    Gtk.main()
