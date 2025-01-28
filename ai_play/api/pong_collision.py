from .utils import Vector2D, get_line_intersection
import logging, math, random
from django.conf import settings
from django.utils import timezone
import math
from ai_play.settings import GAME_CONSTANTS
from datetime import timedelta

class PongGame:
	def __init__(self, match_id, player1_id, creator_username):
		self.match_id = match_id
		self.GAME_WIDTH = settings.GAME_CONSTANTS['GAME_WIDTH']
		self.GAME_HEIGHT = settings.GAME_CONSTANTS['GAME_HEIGHT']
		self.GAME_HALF_WIDTH = self.GAME_WIDTH / 2
		self.GAME_HALF_HEIGHT = self.GAME_HEIGHT / 2
		self.PADDLE_HALF_HEIGHT = settings.GAME_CONSTANTS['PADDLE_HEIGHT'] / 2 # adjusted for a half
		self.PADDLE_HALF_WIDTH = settings.GAME_CONSTANTS['PADDLE_WIDTH'] / 2 # adjusted for a half
		self.PADDLE_SPEED = settings.GAME_CONSTANTS['PADDLE_SPEED']
		self.paddle1 = Paddle(x=-80 + self.PADDLE_HALF_WIDTH, game=self)
		self.paddle2 = Paddle(x=80 - self.PADDLE_HALF_WIDTH, game=self)
		self.ball = Ball()
		self.player1 = Player(player1_id, creator_username)
		self.player2 = AIPlayer(settings.GAME_CONSTANTS['MAX_SCORE'], self.paddle2.paddle_half_height)
		self.start_timestamp = timezone.now()
		self.last_frame = self.start_timestamp
		self.game_start = None

	def __repr__(self):
		return (f"PongGame(match_id={self.match_id}, player1={self.player1}, player2={self.player2}")
	
	def reset(self):
		self.paddle1 = Paddle(x=-80 + self.PADDLE_HALF_WIDTH, game=self)
		self.paddle2 = Paddle(x=80 - self.PADDLE_HALF_WIDTH, game=self)
		self.ball = Ball()

	def set_game_start_time(self, seconds_to_start = 5):
		self.game_start = timezone.now() + timedelta(seconds=seconds_to_start)
		return self.game_start
	
	def get_seconds_until_game_start(self):
		return (self.game_start - timezone.now()).total_seconds()

class Paddle:
	def __init__(self, x, game):
		self.position = Vector2D(x, 0)
		self.paddle_half_height = game.PADDLE_HALF_HEIGHT
		self.paddle_half_width = game.PADDLE_HALF_WIDTH
		self.paddle_speed = game.PADDLE_SPEED

	def __repr__(self):
		return f"Paddle(x={self.position.x}, y={self.position.y}, paddle_half_height={self.paddle_half_height}, paddle_half_width={self.paddle_half_width}, paddle_speed={self.paddle_speed})"

class Ball:
	def __init__(self):
		self.position = Vector2D(0, 0)
		self.speed = settings.GAME_CONSTANTS['BALL_SPEED']
		self.direction = Vector2D(random.choice([-1, 1]), random.choice([-1, 1]))
		self.size = settings.GAME_CONSTANTS['BALL_SIZE']
	
	def __repr__(self):
		return f"Ball(x={self.position.x}, y={self.position.y}, speed={self.speed}, direction={self.direction.x},{self.direction.y})"

class Player:
	def __init__(self, player_id, username):
		self.id = player_id
		self.username = username
		self.score = 0

	def __repr__(self):
		return f"Player(id={self.id}, username={self.username})"
	
class Prediction:
	def __init__(self):
		self.direction = Vector2D(0, 0)
		self.position = Vector2D(0, 0)
		self.exact_position = Vector2D(0, 0)
		self.since = 0
		self.size = 0

class AILevel:
	def __init__(self, reaction, error):
		self.reaction = reaction
		self.error = error

	def __repr__(self):
		return f"AILevl(reaction={self.reaction}, error={self.error})"

# max_score = 5
		#	{"aiReaction": 0.1, "aiError":  60},  # 0: ai is losing by 4
		#	{"aiReaction": 0.2, "aiError":  70},  # 1: ai is losing by 3
		#	{"aiReaction": 0.3, "aiError":  80},  # 2: ai is losing by 2
		#	{"aiReaction": 0.4, "aiError":  90},  # 3: ai is losing by 1
		#	{"aiReaction": 0.5, "aiError":  100}, # 4: tie
		#	{"aiReaction": 0.6, "aiError": 110},  # 5: ai is winning by 1
		#	{"aiReaction": 0.7, "aiError": 120},  # 6: ai is winning by 2
		#	{"aiReaction": 0.8, "aiError": 130},  # 7: ai is winning by 3
		#	{"aiReaction": 0.9, "aiError": 140},  # 8: ai is winning by 4

# max_score = 3
		#	{"aiReaction": 0.1, "aiError":  60},  # 0: ai is losing by 2
		#	{"aiReaction": 0.2, "aiError":  70},  # 1: ai is losing by 1
		#	{"aiReaction": 0.3, "aiError":  80},  # 2: tie
		#	{"aiReaction": 0.4, "aiError":  90},  # 3: ai is winning by 1
		#	{"aiReaction": 0.5, "aiError":  100}, # 4: winning by 2

class AIPlayer:
	def __init__(self, level, paddle_half_height):
		self.levels = []
		self.levels = self.set_initial_levels(level)
		self.level = self.levels[level - 1]
		self.username = "AI"
		self.score = 0
		self.prediction = None
		self.paddle_half_height = paddle_half_height
		self.target_range = []
		self.target_range = self.set_target_range()

	def predict(self, dt, ball, paddle, match_room):
		# only re-predict if the ball changed direction, or its been some amount of time since last prediction
		if (
			self.prediction and self.prediction.position and
			(self.prediction.direction.x * ball.direction.x) > 0 and
			(self.prediction.direction.y * ball.direction.y) > 0 and
			(self.prediction.since < self.level.reaction)
		):
			self.prediction.since += dt
			return
		self.prediction = Prediction()
		paddle_left = paddle.position.x - paddle.paddle_half_width
		# assume collision point on ball_left
		collision_point = Vector2D(ball.position.x + (ball.size / 2), ball.position.y)
		#collision_point = ball_collision_point(ball)
		far_collision_point = collision_point + (ball.direction * 10000) # QUESTION - is such an arbitrary number ok?
		
		pt = get_line_intersection(paddle_left, -10000, paddle_left, 10000, collision_point.x, collision_point.y, far_collision_point.x, far_collision_point.y)
		
		if (pt):
			pt.x -= (ball.size / 2) # adjust back from ball_left
			court_top = match_room.GAME_HALF_HEIGHT * (-1) + ball.size / 2
			court_bottom = match_room.GAME_HALF_HEIGHT - ball.size / 2
			while pt.y < court_top or pt.y > court_bottom:
				if pt.y < court_top:
					pt.y = court_top + (court_top - pt.y)
				elif pt.y > court_bottom:
					pt.y = court_bottom - (pt.y - court_bottom)
			self.prediction.exact_position = pt

			if (ball.direction.x > 0):
				closeness = (ball.position.x - paddle_left) / match_room.GAME_WIDTH
			else:
				closeness = (paddle_left - ball.position.x) / match_room.GAME_WIDTH # never happens now, should be changed to paddle_right for AI vs AI
			error = self.level.error * closeness
			self.prediction.position = Vector2D(pt.x, pt.y + random.uniform(-error, error))
			self.prediction.since = 0
			self.prediction.direction = ball.direction
			logging.info(f"AI prediction: {self.prediction.position}")
		else:
			self.position = Vector2D(0, 0)
			self.exact_position = Vector2D(0, 0)

	def move_ai_paddle(self, paddle, match_room):
		if not self.prediction.position:
			return

		if self.prediction.position.y < paddle.position.y - abs(self.target_range[0]): 
			if paddle.position.y > (match_room.GAME_HALF_HEIGHT - paddle.paddle_half_height) * (-1):
				paddle.position.y -= paddle.paddle_speed
		elif self.prediction.position.y > paddle.position.y + abs(self.target_range[1]):
			if paddle.position.y < (match_room.GAME_HALF_HEIGHT - paddle.paddle_half_height):
				paddle.position.y += paddle.paddle_speed

	def set_initial_levels(self, max_score):
		levels = []
		reaction = 0.2
		error = 10
		num_of_levels = (max_score - 1) * 2 + 1
		while (num_of_levels > 0):
			new_level = AILevel(reaction, error)
			reaction += 0.1
			error += 20
			levels.append(new_level)
			num_of_levels -= 1
		logging.info(f"Setting these levels: {levels}")
		return levels

	def update_level(self, ai_player_score, other_player_score):
		if (ai_player_score == GAME_CONSTANTS['MAX_SCORE'] or other_player_score == GAME_CONSTANTS['MAX_SCORE']):
			return
		neutral_level = (len(self.levels) // 2) # integer division to avoid indexing with floats
		# logging.info(f"Neutral level: {neutral_level}") # should be the level in the middle
		if ai_player_score == other_player_score:
			self.level = self.levels[neutral_level]
		elif ai_player_score > other_player_score:
			self.level = self.levels[neutral_level + (ai_player_score - other_player_score)]
		elif ai_player_score < other_player_score:
			self.level = self.levels[neutral_level - (other_player_score - ai_player_score)]

	def set_target_range(self):
		range_points = [0 - self.paddle_half_height, (0 - self.paddle_half_height / 2) , 0, (0 + self.paddle_half_height / 2), 0 + self.paddle_half_height]
		target_range = random.sample(range_points, 2)
		target_range.sort()
		logging.info(f"AI initial target range: {target_range[0], target_range[1]}")
		return target_range

	def __repr__(self):
		return f"AIPlayer (username={self.username}, levels={self.levels})"


def ball_collision_point(ball: Ball) -> Vector2D:
	theta = math.atan2(ball.direction.y, ball.direction.x)
	x = (ball.size / 2) * math.cos(theta)
	y = (ball.size / 2) * math.sin(theta)
	collision_point = Vector2D(x, y) + ball.position
	return collision_point

# Calculate the rebound angle based on the impact point relative to the paddle's center.
def calculate_rebound_angle(paddle, ball, max_angle=55) -> float:

	# Calculate the vertical distance between the paddle's center and the ball's position
	# The result will be a range of -half_paddle_height to half_paddle_height
	relative_intersect_y = paddle.position.y - ball.position.y

	# Normalize the distance to a range of -1 to 1
	normalized_relative_intersection_y = relative_intersect_y / paddle.paddle_half_height

	# Determine the bounce anfle based on the ball's direcction
	if (ball.direction.y < 0): # ball going up
		bounce_angle = normalized_relative_intersection_y * max_angle
	elif (ball.direction.y >= 0): # ball going down
		bounce_angle = normalized_relative_intersection_y * -max_angle
	if (abs(bounce_angle) < 15):
		if (bounce_angle < 0):
			bounce_angle = -15
		else:
			bounce_angle = 15
	return (bounce_angle)

def calculate_ball_direction_after_collision(paddle, ball) -> Vector2D:
		
		new_ball_direction = Vector2D(0,0)

		# Calculate the rebound angle
		rebound_angle = calculate_rebound_angle(paddle, ball)

		# Determine the new y-direction based on the ball's position relative to the paddle
		if (ball.position.y > paddle.position.y):
			new_ball_direction.y = -math.sin(math.radians(-rebound_angle)) # ball hit paddle in the bottom half
		else:
			new_ball_direction.y = -math.sin(math.radians(rebound_angle)) # ball hit paddle in the top half

		# Determine the new x-direction based on the ball's position
		if (ball.position.x > 0):
			new_ball_direction.x = -math.cos(math.radians(rebound_angle)) # ball hit on the right paddle
		else:
			new_ball_direction.x = math.cos(math.radians(rebound_angle)) # ball hit on the left paddle
		return new_ball_direction

def paddle_collision(ball: Ball, paddle1: Paddle, paddle2: Paddle, ai_player: AIPlayer) -> Ball:
	speed_constant = 0.1
	# top & bottom are y-components, left & right are x-components
	paddle1_top = paddle1.position.y - paddle1.paddle_half_height
	paddle1_bottom = paddle1.position.y + paddle1.paddle_half_height 
	paddle1_right = paddle1.position.x + paddle1.paddle_half_width
	paddle1_left = paddle1.position.x - paddle1.paddle_half_width

	paddle2_top = paddle2.position.y - paddle2.paddle_half_height
	paddle2_bottom = paddle2.position.y + paddle2.paddle_half_height
	paddle2_right = paddle2.position.x + paddle2.paddle_half_width
	paddle2_left = paddle2.position.x - paddle2.paddle_half_width

	ball_top = ball.position.y - (ball.size / 2)
	ball_bottom = ball.position.y + (ball.size / 2)
	ball_right = ball.position.x + (ball.size / 2)
	ball_left = ball.position.x - (ball.size / 2)

	ball_next_step_left = Vector2D(ball_left, ball.position.y) + (ball.direction * ball.speed)
	ball_next_step_right = Vector2D(ball_right, ball.position.y) + (ball.direction * ball.speed)
	ball_next_step_down = Vector2D(ball.position.x, ball_bottom) + (ball.direction * ball.speed)
	ball_next_step_up = Vector2D(ball.position.x, ball_top) + (ball.direction * ball.speed)
		
	# compute ball collision point for corners
	collision_point = ball_collision_point(ball)
	ball_collision_next = collision_point + (ball.direction * ball.speed)

	if intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, ball_left, ball.position.y, ball_next_step_left.x, ball_next_step_left.y):
		logging.info("Paddle1 side")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle1, ball)
		ball.speed += speed_constant
		ai_player.set_target_range()
	elif intersection := get_line_intersection(paddle1_right, paddle1_top, paddle1_left, paddle1_top, ball.position.x, ball_bottom, ball_next_step_down.x, ball_next_step_down.y):
		logging.info("Paddle1 top")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_left, paddle1_bottom, ball.position.x, ball_top, ball_next_step_up.x, ball_next_step_up.y):
		logging.info("Paddle1 bottom")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle1_right, paddle1_top, paddle1_left, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 top - top corner")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 side - top corner")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle1, ball)
		ball.speed += speed_constant
		ai_player.set_target_range()
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_left, paddle1_bottom, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 bottom - bottom corner")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 side - bottom corner")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle1, ball)
		ball.speed += speed_constant
		ai_player.set_target_range()
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, ball_right, ball.position.y, ball_next_step_right.x, ball_next_step_right.y):
		logging.info("Paddle2 side")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle2, ball)
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_top, paddle2_right, paddle2_top, ball.position.x, ball_bottom, ball_next_step_down.x, ball_next_step_down.y):
		logging.info("Paddle2 top")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_right, paddle2_bottom, ball.position.x, ball_top, ball_next_step_up.x, ball_next_step_up.y):
		logging.info("Paddle2 bottom")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_top, paddle2_right, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 top - top corner")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 side - top corner")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle2, ball)
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_right, paddle2_bottom, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 bottom - bottom corner")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += speed_constant
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 side - bottom corner")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle2, ball)
		ball.speed += speed_constant
	return ball