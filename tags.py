#!/usr/bin/python
import gtk
import difflib
"""
This plugin provide tag compleation menu,
if you want to customize matching function
replace fuzzy_match with your's
"""
#TODO:
#[done]smart filter (fuzzy):
#[done] you write clr, it matches color, clear, etc
#redfactor fuzzy_match()
#[done]show popup near the text
#[done]refactoring of code
#colorizing matched
#inline completion
#[done]if only one - insert
#[done]generate list of all tags in place


class TagCompl:
    def activate(self, plugin_api):
        self.api = plugin_api
        self.req = self.api.get_requester()

    def onTaskOpened(self, plugin_api):
            self.taskview = plugin_api.textview
            self.taskview.connect('key-press-event', self.tab_pressed)
            self.buf = self.taskview.buff

    def deactivate(self, plugin_api):
        print "the plugin was deactivated"

    def get_names_of_all_tags(self):
        #tags = self.api.get_all_tags()
        tags = self.req.get_used_tags()
        return [tag.get_attribute('name') for tag in tags]

    def complete(self, completion):
        """Insert selected suggestion"""
        self.buf.delete(self.start, self.stop)
        self.buf.insert(self.stop, completion)

    def on_item_select(self, widget, tag):
        """Handler for tag selecte event in compleation menu"""
        self.complete(tag)

    def make_compl_menu(self, suggestions):
        """Fill menu with items
        Params:
            suggestions: list of menu items
        """
        popupMenu = gtk.Menu()
        #fill it
        for tag in suggestions:
            item = gtk.MenuItem(label=tag)
            item.connect('activate', self.on_item_select, tag)
            item.show()
            popupMenu.append(item)
        return popupMenu

    def place_at_cursor(self, data):
        """Return coordinates of cursos"""
        textview_coord = self.taskview.get_iter_location(self.start)
        win_x, win_y = self.taskview.get_window(gtk.TEXT_WINDOW_WIDGET).get_origin()
        x = textview_coord.x + win_x + 5
        y = textview_coord.y + win_y
        return x, y, False

    def tab_pressed(self, widget, event):
        """Main handler"""
        if event.keyval == gtk.keysyms.Tab:
            self.start = self.buf.get_iter_at_mark(self.buf.get_insert())
            self.stop = get_tag_start_pos(self.start)
            # if not tag (not starts with @)
            if not self.stop:
                return
            # make the suggestions list
            written = self.buf.get_text(self.stop, self.start).lower()
            tags_names = self.get_names_of_all_tags()
            # try to remove already written part of tag from tags list
            # because gtg use live update of your writing
            try:
                tags_names.remove(written)
            except ValueError:
                pass
            suggestions = fuzzy_match(written, tags_names)
            # if only one or no suggestions
            if len(suggestions) == 1:
                self.complete(suggestions[0])
                return True
            elif not suggestions:
                return
            # make & show completion menu
            popup_menu = self.make_compl_menu(suggestions)
            popup_menu.popup(None, None, self.place_at_cursor, 0, 0)
            return True


def get_tag_start_pos(cur_pos):
    """Return position where tag begins
    | <- means cursor position:
        @tag1 @tag2|
    will return this position:
        @tag1 |@tag2
    """
    cur_pos = cur_pos.copy()
    while cur_pos.get_char() != '@':
        if cur_pos.get_char() == " ":
            return
        cur_pos.backward_chars(1)
    return cur_pos


def fuzzy_match(token, all_tokens):
    """At first we filter tokens throw simple filter (a in b) to define if there are
    single match or match all tags (tab pressed after @)
    """
    a_in_b_suggestions = filter(lambda lst: token in lst, all_tokens)
    # if only one candidate return it
    if len(a_in_b_suggestions) == 1:
        return a_in_b_suggestions
    fuzzy_suggestions = difflib.get_close_matches(token, all_tokens)
    suggestions = set(a_in_b_suggestions) | set(fuzzy_suggestions)
    return list(suggestions)
