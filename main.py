import gi
gi.require_version('Gtk', '3.0')
from gi.repository import Gtk, Gdk, GLib, Pango
import google.generativeai as genai
import google.api_core.exceptions
import os
import sys
from dotenv import load_dotenv

load_dotenv()

# --- Configuration ---
class Config:
    GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
    GEMINI_MODEL = 'gemini-2.5-flash'
    INITIAL_WIDTH = 600
    INITIAL_HEIGHT = 50
    MAX_HEIGHT = 800
    FONT_FAMILY = "monospace"
    FONT_SIZE = "14pt"
    PADDING = "5px"
    PROMPT = "> "

# --- Gemini API Setup ---
if not Config.GEMINI_API_KEY:
    print("Error: GEMINI_API_KEY not found in .env file.", file=sys.stderr)
    sys.exit(1)

genai.configure(api_key=Config.GEMINI_API_KEY)
model = genai.GenerativeModel(Config.GEMINI_MODEL)
chat = model.start_chat(history=[])

class AiLauncher(Gtk.Window):
    def __init__(self):
        Gtk.Window.__init__(self, title="AI Launcher")
        self.set_decorated(False)
        self.set_keep_above(True)
        
        self.set_default_size(Config.INITIAL_WIDTH, Config.INITIAL_HEIGHT)
        self.conversation_complete = False
        self.ai_response_start_mark = None

        self.connect("focus-out-event", self.on_focus_out)
        self.connect("key-press-event", self.on_window_key_press)

        self.textview = Gtk.TextView()
        self.textview.set_wrap_mode(Gtk.WrapMode.WORD_CHAR)
        self.textview.connect("key-press-event", self.on_textview_key_press)
        self.textview.set_top_margin(12)
        self.buffer = self.textview.get_buffer()
        
        self.scrolled_window = Gtk.ScrolledWindow()
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.scrolled_window.connect("size-allocate", self.on_size_allocated)
        self.scrolled_window.add(self.textview)
        self.add(self.scrolled_window)

        self.load_css()
        self.create_tags()
        self.position_in_center()
        self.show_all()
        self.textview.grab_focus()
        self.insert_prompt()

    def position_in_center(self):
        display = self.get_display()
        monitor = display.get_primary_monitor() or display.get_monitor(0)
        workarea = monitor.get_geometry()
        win_width, win_height = self.get_size()
        x = workarea.x + (workarea.width - win_width) // 2
        y = workarea.y + (workarea.height * 0.25)  # 25% from the top
        self.move(x, int(y))

    def load_css(self):
        css_provider = Gtk.CssProvider()
        css = f"""
        window {{ background-color: rgba(0, 0, 0, 0.9); }}
        textview, text {{
            background-color: transparent;
            color: white;
            font-family: {Config.FONT_FAMILY};
            font-size: {Config.FONT_SIZE};
        }}
        scrolledwindow {{ background-color: transparent; }}
        textview {{ padding: {Config.PADDING}; }}
        """.encode('utf-8')
        css_provider.load_from_data(css)
        context = self.get_style_context()
        screen = Gdk.Screen.get_default()
        context.add_provider_for_screen(screen, css_provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

    def create_tags(self):
        self.buffer.create_tag("user_tag", foreground="#ffffff")
        self.buffer.create_tag("ai_tag", foreground="#ffffff")
        self.buffer.create_tag("prompt_tag", foreground="#ffffff")
        self.buffer.create_tag("uneditable", editable=False)
        self.buffer.create_tag("error_tag", foreground="#ff4444", weight=Pango.Weight.BOLD)

    def insert_prompt(self):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(end_iter, Config.PROMPT, "prompt_tag")
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

            if self.handle_command(user_text):
                Gtk.main_quit()
                return True

            if user_text:
                self.conversation_complete = False
                self.buffer.apply_tag_by_name("user_tag", start_iter, end_iter)
                GLib.idle_add(self.get_ai_response, user_text)
            return True
        
        return False

    def handle_command(self, text):
        if text == "/b":
            os.system("x-www-browser &")
            return True
        if text == "/f":
            os.system("thunar &")
            return True
        if text == "/t":
            os.system("xfce4-terminal &")
            return True
        return False

    def reset_for_new_query(self, initial_char):
        self.buffer.set_text("")
        self.resize(Config.INITIAL_WIDTH, Config.INITIAL_HEIGHT)
        self.scrolled_window.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)
        self.insert_prompt()
        self.buffer.insert(self.buffer.get_end_iter(), initial_char)
        self.conversation_complete = False

    def get_ai_response(self, user_text):
        try:
            self.textview.set_editable(False) # Disable editing during response
            response_stream = chat.send_message(user_text, stream=True)
            self.buffer.insert(self.buffer.get_end_iter(), "\n\n")
            # Mark the start of the AI's response so we can scroll to it
            self.ai_response_start_mark = self.buffer.create_mark(
                "ai_start", self.buffer.get_end_iter(), left_gravity=True
            )
            GLib.idle_add(self.process_stream, response_stream)
        except google.api_core.exceptions.GoogleAPICallError as e:
            self.append_message(f"API Error: {e.message}", "error_tag", done=True)
        except Exception as e:
            self.append_message(f"An unexpected error occurred: {e}", "error_tag", done=True)
        return False # Important to return False from the initial GLib.idle_add call

    def process_stream(self, stream):
        try:
            for chunk in stream:
                if chunk.text:
                    self.append_message(chunk.text, "ai_tag", done=False)
            # Signal that the stream is complete
            self.stream_complete()
        except Exception as e:
            self.append_message(f"\nAn error occurred during streaming: {e}", "error_tag", done=True)
        return False # Stop the GLib.idle_add timer

    def append_message(self, message, tag_name, done=True):
        end_iter = self.buffer.get_end_iter()
        self.buffer.insert_with_tags_by_name(end_iter, message, tag_name)
        self.resize_window()
        # Scroll to the beginning of the AI response, not the end
        if self.ai_response_start_mark:
            start_iter = self.buffer.get_iter_at_mark(self.ai_response_start_mark)
            self.textview.scroll_to_iter(start_iter, 0.0, True, 0.0, 0.0)
        if done:
            self.stream_complete()

    def stream_complete(self):
        # Clean up the mark
        if self.ai_response_start_mark:
            self.buffer.delete_mark(self.ai_response_start_mark)
            self.ai_response_start_mark = None
        self.insert_prompt()
        self.resize_window()
        self.conversation_complete = True
        self.textview.set_editable(True) # Re-enable editing

    def resize_window(self):
        # Force GTK to update the layout to get the correct height
        while Gtk.events_pending():
            Gtk.main_iteration()

        vadjustment = self.scrolled_window.get_vadjustment()
        # The adjustment's upper value is the total height of the content
        desired_height = int(vadjustment.get_upper())

        # Add the textview's vertical margins for a better fit
        desired_height += self.textview.get_top_margin() + self.textview.get_bottom_margin()

        new_height = min(desired_height, Config.MAX_HEIGHT)
        new_height = max(Config.INITIAL_HEIGHT, new_height)

        self.resize(Config.INITIAL_WIDTH, new_height)

    def on_size_allocated(self, widget, allocation):
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