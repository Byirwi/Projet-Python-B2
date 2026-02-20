import random
import pygame
from Config import MAP_WIDTH, MAP_HEIGHT
from Game.Powerups.PowerUp import PowerUp


class PowerUpManager:
    def __init__(self):
        self.rng = random.Random()
        self.powerups = []
        self.last_spawn_ms = 0
        self.spawn_interval_ms = 5000
        self.powerup_lifetime_ms = 12000
        self.max_powerups = 3

        self._spawned_at = {}
        self._active_effects = {}
        self._base_speeds = {}

    def _register_tank(self, tank):
        tank_id = id(tank)
        if tank_id not in self._base_speeds:
            self._base_speeds[tank_id] = tank.speed
        if tank_id not in self._active_effects:
            self._active_effects[tank_id] = {}

    def _spawn_random_powerup(self, solid_obstacles):
        power_type = self.rng.choice(["heal", "speed"])

        for _ in range(40):
            x = self.rng.randint(40, MAP_WIDTH - 40)
            y = self.rng.randint(40, MAP_HEIGHT - 40)
            candidate = PowerUp(power_type, x, y)

            blocked = any(candidate.rect.colliderect(obs) for obs in solid_obstacles)
            occupied = any(candidate.rect.colliderect(existing.rect.inflate(14, 14)) for existing in self.powerups)

            if not blocked and not occupied:
                return candidate

        return None

    def _apply_pickup(self, tank, powerup, now_ms):
        tank_id = id(tank)

        if powerup.power_type == "heal":
            tank.health = min(100, tank.health + 25)
            return

        # speed boost
        self._active_effects[tank_id]["speed"] = now_ms + 6000
        self._apply_effects_to_tank(tank, now_ms)

    def _apply_effects_to_tank(self, tank, now_ms):
        tank_id = id(tank)
        effects = self._active_effects.get(tank_id, {})
        base_speed = self._base_speeds.get(tank_id, tank.speed)

        speed_end = effects.get("speed")
        if speed_end and now_ms < speed_end:
            tank.speed = base_speed * 1.6
        else:
            if "speed" in effects:
                del effects["speed"]
            tank.speed = base_speed

    def update(self, tank, solid_obstacles):
        now_ms = pygame.time.get_ticks()
        self._register_tank(tank)

        # Spawn périodique
        if len(self.powerups) < self.max_powerups and now_ms - self.last_spawn_ms >= self.spawn_interval_ms:
            new_powerup = self._spawn_random_powerup(solid_obstacles)
            if new_powerup:
                self.powerups.append(new_powerup)
                self._spawned_at[id(new_powerup)] = now_ms
                self.last_spawn_ms = now_ms

        # Expiration des powerups au sol
        alive = []
        for powerup in self.powerups:
            born_ms = self._spawned_at.get(id(powerup), now_ms)
            if now_ms - born_ms < self.powerup_lifetime_ms:
                alive.append(powerup)
            else:
                self._spawned_at.pop(id(powerup), None)
        self.powerups = alive

        # Pickup
        tank_rect = pygame.Rect(tank.x, tank.y, tank.width, tank.height)
        remaining = []
        for powerup in self.powerups:
            if tank_rect.colliderect(powerup.rect):
                self._apply_pickup(tank, powerup, now_ms)
                self._spawned_at.pop(id(powerup), None)
            else:
                remaining.append(powerup)
        self.powerups = remaining

        # Effets actifs
        self._apply_effects_to_tank(tank, now_ms)

    def draw(self, screen, camera_x, camera_y):
        for powerup in self.powerups:
            powerup.draw(screen, camera_x, camera_y)

    def draw_hud(self, screen, font_small, tank, x=10, y=120):
        now_ms = pygame.time.get_ticks()
        effects = self._active_effects.get(id(tank), {})

        speed_end = effects.get("speed")
        if speed_end and speed_end > now_ms:
            sec_left = max(0.0, (speed_end - now_ms) / 1000.0)
            txt = font_small.render(f"Boost vitesse: {sec_left:.1f}s", True, (120, 210, 255))
            screen.blit(txt, (x, y))
