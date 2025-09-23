import traceback

from tasks.base.assets.assets_base_page import *


class Page:
    # Key: str, page name like "page_main"
    # Value: Page, page instance
    all_pages = {}

    @classmethod
    def clear_connection(cls):
        for page in cls.all_pages.values():
            page.parent = None

    @classmethod
    def init_connection(cls, destination):
        """
        Initialize an A* path finding among pages.

        Args:
            destination (Page):
        """
        cls.clear_connection()

        visited = [destination]
        visited = set(visited)
        while 1:
            new = visited.copy()
            for page in visited:
                for link in cls.iter_pages():
                    if link in visited:
                        continue
                    if page in link.links:
                        link.parent = page
                        new.add(link)
            if len(new) == len(visited):
                break
            visited = new

    @classmethod
    def iter_pages(cls):
        return cls.all_pages.values()

    @classmethod
    def iter_check_buttons(cls):
        for page in cls.all_pages.values():
            yield page.check_button

    def __init__(self, check_button):
        self.check_button = check_button
        self.links = {}
        (filename, line_number, function_name, text) = traceback.extract_stack()[-2]
        self.name = text[:text.find('=')].strip()
        self.parent = None
        Page.all_pages[self.name] = self

    def __eq__(self, other):
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name

    def link(self, button, destination):
        self.links[destination] = button


# Main page
# page_main = Page(MAIN_GOTO_CHARACTER)
page_main = Page(MAIN_PAGE)
# page_home = Page(MAIN_PAGE)

# Menu, entered from phone
page_menu = Page(MENU_CHECK)
page_menu.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_MENU, destination=page_menu)

# Character
page_character = Page(CHARACTER_CHECK)
page_character.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_CHARACTER, destination=page_character)

# Team
page_team = Page(TEAM_CHECK)
page_team.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_TEAM, destination=page_team)

# Item, storage
page_item = Page(ITEM_CHECK)
page_item.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_ITEM, destination=page_item)

# Guide, which includes beginners' guide, daily missions and dungeons
page_guide = Page(GUIDE_CHECK)
page_guide.link(GUIDE_CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_GUIDE, destination=page_guide)

# Gacha
page_gacha = Page(GACHA_CHECK)
page_gacha.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_GACHA, destination=page_gacha)

# Battle Pass
page_battle_pass = Page(BATTLE_PASS_CHECK)
page_battle_pass.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_BATTLE_PASS, destination=page_battle_pass)

# Event
page_event = Page(EVENT_CHECK)
page_event.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_EVENT, destination=page_event)

# Map
page_map = Page(MAP_CHECK)
page_map.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_MAP, destination=page_map)

# page_world, subpage of map, used to choose a world/planet e.g. Herta Space Station
page_world = Page(WORLD_CHECK)
page_world.link(BACK, destination=page_map)
page_map.link(MAP_GOTO_WORLD, destination=page_world)

# Tutorial
page_tutorial = Page(TUTORIAL_CHECK)
page_tutorial.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_TUTORIAL, destination=page_tutorial)

# Mission
page_mission = Page(MISSION_CHECK)
page_mission.link(CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_MISSION, destination=page_mission)

# Message
page_message = Page(MESSAGE_CLOSE)
page_message.link(MESSAGE_CLOSE, destination=page_main)
page_main.link(MAIN_GOTO_MESSAGE, destination=page_message)

# Camera
page_camera = Page(CAMERA_CHECK)
page_camera.link(CLOSE, destination=page_menu)
page_menu.link(MENU_GOTO_CAMERA, destination=page_camera)

# Synthesize
page_synthesize = Page(SYNTHESIZE_CHECK)
page_synthesize.link(CLOSE, destination=page_menu)
page_menu.link(MENU_GOTO_SYNTHESIZE, destination=page_synthesize)

# Assignment
page_assignment = Page(ASSIGNMENT_CHECK)
page_assignment.link(CLOSE, destination=page_main)
page_menu.link(MENU_GOTO_ASSIGNMENT, destination=page_assignment)

# Forgotten Hall
page_forgotten_hall = Page(FORGOTTEN_HALL_CHECK)
page_forgotten_hall.link(CLOSE, destination=page_main)

# Rogue, Simulated Universe
page_rogue = Page(ROGUE_CHECK)
page_rogue.link(CLOSE, destination=page_main)

# Planner result
page_planner = Page(PLANNER_CHECK)
page_planner.link(CLOSE, destination=page_menu)


# FX
page_main = Page(MAIN_PAGE)
page_reward = Page(REWARD_CHECK)

page_reward.link(REWARD_CHECK_CLOSE, destination=page_main)
page_main.link(REWARD_CHECK_OPEN, destination=page_reward)

page_refinery = Page(REFINERY)
page_reward.link(REFINERY_OPEN, destination=page_refinery)
page_refinery.link(HOME_BUTTON, destination=page_main)

page_refinery_schedule = Page(REFINERY_SCHEDULE_PAGE)
page_refinery.link(SCHEDULE_BUTTON, destination=page_refinery_schedule)

page_convenience_store = Page(CONVENIENCE_STORE)
page_convenience_store.link(HOME_BUTTON, destination=page_main)
page_reward.link(CONVENIENCE_STORE_OPEN, destination=page_convenience_store)

page_convenience_store_schedule = Page(CONVENIENCE_STORE_SCHEDULE_PAGE)
page_convenience_store.link(SCHEDULE_BUTTON, destination=page_convenience_store_schedule)

page_naval_port = Page(NAVAL_PORT_PAGE)
page_main.link(NAVAL_PORT_BUTTON, destination=page_naval_port)
page_naval_port.link(HOME_BUTTON, destination=page_main)

page_quiz_center = Page(QUIZ_CENTER_PAGE)
page_naval_port.link(QUIZ_CENTER_BUTTON, destination=page_quiz_center)
page_quiz_center.link(HOME_BUTTON, destination=page_main)

page_main_line = Page(MAIN_LINE_PAGE)
page_main.link(ATTACK_BUTTON, destination=page_main_line)
page_main_line.link(HOME_BUTTON, destination=page_main)

page_exercise = Page(EXERCISE_PAGE)
page_main_line.link(EXERCISE_BUTTON, destination=page_exercise)
page_exercise.link(HOME_BUTTON, destination=page_main)

page_competition = Page(COMPETITION_PAGE)
page_main_line.link(COMPETITION_BUTTON, destination=page_competition)
page_competition.link(HOME_BUTTON, destination=page_main)
page_exercise.link(COMPETITION_BUTTON, destination=page_competition)
page_competition.link(EXERCISE_BUTTON, destination=page_exercise)

page_arena = Page(ARENA_PAGE)
page_arena.link(HOME_BUTTON, destination=page_main)

page_daily_routine = Page(DAILY_ROUTINE_PAGE)
page_daily_routine.link(HOME_BUTTON, destination=page_main)
page_main_line.link(DAILY_ROUTINE_BUTTON, destination=page_daily_routine)

page_expedition = Page(EXPEDITION_PAGE)
page_expedition.link(HOME_BUTTON, destination=page_main)
page_reward.link(EXPEDITION_BUTTON, destination=page_expedition)

page_beach = Page(BEACH_PAGE)
page_beach.link(HOME_BUTTON, destination=page_main)
page_reward.link(BEACH_BUTTON, destination=page_beach)

# page_default = Page(HOME_BUTTON)
# page_default.link(HOME_BUTTON, destination=page_main)

page_daily_reward = Page(DAILY_REWARD)
page_daily_reward.link(DAILY_REWARD, destination=page_main)

page_temp = Page(BEACH_START_TRAINING)
page_temp.link(HOME_BUTTON, destination=page_main)

page_stage_failed = Page(STAGE_FAILED_PAGE)
page_stage_failed.link(STAGE_FAILED_PAGE, destination=page_main_line)