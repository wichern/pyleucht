
import random
import pyleucht as pl

class PiggyGame(pl.state.Base):
    BUTTON_START = pl.button.BUTTON_TOP_MIDDLE
    BUTTON_BACK = pl.button.BUTTON_BOTTOM_MIDDLE
    BUTTON_JUMP = pl.button.BUTTON_TOP_RIGHT

    COLOR_TIE = pl.RGB(255, 255, 255)
    COLOR_AHEAD = pl.RGB(0, 255, 0)
    COLOR_BEHIND = pl.RGB(255, 0, 0)

    LABEL_OFFSET_Y = 3

    SPEED = 8

    def __init__(self, screen: type[pl.screen.Base], buttons: type[pl.button.HandlerBase]):
        super().__init__(screen, buttons)

        # Blue sky
        skybox = pl.BBox(pl.Point(0, 0), pl.Point(screen.width, screen.height - 1))
        self.animations.append(pl.animation.FillColor(pl.RGB(160, 160, 255), bbox=skybox))

        # Clouds
        self.clouds = []
        cloud_sprite = pl.animation.Sprite("extras/sprites/piggy/cloud0.png")
        cloud_animations = {"idle": pl.animation.SpriteAnimation([cloud_sprite], 1.0)}
        cloud = pl.animation.SpriteCharacter(cloud_animations, "idle", pl.Point(screen.width + 10, 1), velocity=pl.Point(self.SPEED // -2, 0))
        self.animations.append(cloud)
        self.clouds.append(cloud)
        for i in range(2):
            cloud_sprite = pl.animation.Sprite("extras/sprites/piggy/cloud1.png")
            cloud_animations = {"idle": pl.animation.SpriteAnimation([cloud_sprite], 1.0)}
            cloud = pl.animation.SpriteCharacter(cloud_animations, "idle", pl.Point(screen.width + i * 15, 1 + i), velocity=pl.Point(self.SPEED // -2, 0))
            self.animations.append(cloud)
            self.clouds.append(cloud)

        # Green lawn
        self.animations.append(pl.animation.HLine(pl.RGB(80, 200, 80), screen.height - 1))

        # Lives
        self.lives_animation = pl.animation.PiggyLives()
        self.animations.append(self.lives_animation)

        # Piggy
        piggy_animations = {
            "run": pl.animation.SpriteAnimation(
                [ pl.animation.Sprite("extras/sprites/piggy/piggy0.png"),
                  pl.animation.Sprite("extras/sprites/piggy/piggy1.png") ],
                4.0),
            "jump": pl.animation.SpriteAnimation(
                [ pl.animation.Sprite("extras/sprites/piggy/piggy_jump.png") ],
                4.0)
        }
        self.piggy = pl.animation.SpriteCharacter(piggy_animations, "run", pl.Point(2, 5))
        self.animations.append(self.piggy)

        # Haystack
        hay_sprite = pl.animation.Sprite("extras/sprites/piggy/hay.png")
        hay_animations = {
            "idle": pl.animation.SpriteAnimation([hay_sprite], 1.0)
        }
        self.haystack = pl.animation.SpriteCharacter(hay_animations, "idle", pl.Point(22, 8), velocity=pl.Point(-self.SPEED, 0))
        self.animations.append(self.haystack)
        
        self.jump_timer = 0.0
        self.piggy_pos_run = pl.Point(4, 5)
        self.piggy_pos_jump = pl.Point(4, 1)
    
    def update(self, dt):
        self.dt = dt
        super().update(dt)
    
    def on_enter(self):
        super().on_enter()
        self.buttons.set_led_state(self.BUTTON_START, True)
        self.buttons.set_led_state(self.BUTTON_BACK, True)
        self.buttons.set_led_state(self.BUTTON_JUMP, True)

        self.lives = 4

    def on_button_pressed(self, event: pl.event.ButtonPressed):
        if event.button_id == self.BUTTON_JUMP and self.piggy.state != "jump":
            self.piggy.set_state("jump")
            self.piggy.pos = self.piggy_pos_jump
            self.jump_timer = 0.5

        if event.button_id == self.BUTTON_BACK:
            return (pl.state.UserAction.BACK, None)

        return (pl.state.UserAction.NONE, None)

    def on_frame(self):
        # Reset clouds when off screen
        for cloud in self.clouds:
            if cloud.pos.x < -cloud.animations["idle"].sprites[0].image.width:
                cloud.pos = pl.Point(int(self.screen.width), int(cloud.pos.y))

        # Reset haystack when off screen
        if self.haystack.pos.x < -self.haystack.animations["idle"].sprites[0].image.width:
            self.haystack.pos.x = int(self.screen.width) + random.randint(10, 30)

        if self.jump_timer > 0:
            self.jump_timer -= self.dt
            if self.jump_timer <= 0:
                self.piggy.set_state("run")
                self.piggy.pos = self.piggy_pos_run
