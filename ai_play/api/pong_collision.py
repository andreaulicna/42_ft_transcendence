from .utils import Vector2D, get_line_intersection
import logging, math, random
from django.conf import settings
from django.utils import timezone
import math


class PongGame:
	def __init__(self, match_id, player1, player2):
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
		self.player1 = player1
		self.player2 = player2
		self.start_timestamp = timezone.now()
		self.last_frame = self.start_timestamp


	# def __repr__(self):
	# 	return (f"PongGame(match_id={self.match_id}, game_width={self.GAME_WIDTH}, "
	# 			f"game_height={self.GAME_HEIGHT}, paddle1={self.paddle1}, paddle2={self.paddle2}, "
	# 			f"player1={self.player1}, player2={self.player2})")
	
	def __repr__(self):
		return (f"PongGame(match_id={self.match_id}, player1={self.player1}, player2={self.player2}")
	
	def reset(self):
		self.paddle1 = Paddle(x=-80 + self.PADDLE_HALF_WIDTH, game=self)
		self.paddle2 = Paddle(x=80 - self.PADDLE_HALF_WIDTH, game=self)
		self.ball = Ball()

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


def ball_collision_point(ball: Ball) -> Vector2D:
	theta = math.atan2(ball.direction.y, ball.direction.x)
	x = (ball.size / 2) * math.cos(theta)
	y = (ball.size / 2) * math.sin(theta)
	collision_point = Vector2D(x, y) + ball.position
	return collision_point

# Calculate the rebound angle based on the impact point relative to the paddle's center.
def calculate_rebound_angle(paddle, ball, max_angle=45) -> float:

	# Calculate the vertical distance between the paddle's center and the ball's position
	# The result will be a range of -half_paddle_height to half_paddle_height
	relativeIntersectY = paddle.position.y - ball.position.y

	# Normalize the distance to a range of -1 to 1
	normalizedRelativeIntersectionY = relativeIntersectY / paddle.paddle_half_height

	# Determine the bounce anfle based on the ball's direcction
	if (ball.direction.y < 0): # ball going up
		bounceAngle = normalizedRelativeIntersectionY * max_angle
	elif (ball.direction.y >= 0): # ball going down
		bounceAngle = normalizedRelativeIntersectionY * -max_angle
	return (bounceAngle)

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

def paddle_collision(ball: Ball, paddle1: Paddle, paddle2: Paddle) -> Ball:
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

	# if -78 < ball.position.x <= -76:
	# 	logging.info(f"paddle1 top left: [{paddle1_left},{paddle1_top}]")
	# 	logging.info(f"paddle1 top right: [{paddle1_right},{paddle1_top}]")
	# 	logging.info(f"paddle1 bottom right: [{paddle1_right},{paddle1_bottom}]")
	# 	logging.info(f"collision point: {collision_point}")
	# 	logging.info(f"ball position:: {ball.position}")
	# 	logging.info(f"next step down: {ball_next_step_down}")
	# 	logging.info(f"next step left: {ball_next_step_left}")

	if intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, ball_left, ball.position.y, ball_next_step_left.x, ball_next_step_left.y):
		logging.info("Paddle1 side")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle1, ball)
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_top, paddle1_left, paddle1_top, ball.position.x, ball_bottom, ball_next_step_down.x, ball_next_step_down.y):
		logging.info("Paddle1 top")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_left, paddle1_bottom, ball.position.x, ball_top, ball_next_step_up.x, ball_next_step_up.y):
		logging.info("Paddle1 bottom")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_top, paddle1_left, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 top - top corner")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 side - top corner")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction.x *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_left, paddle1_bottom, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 bottom - bottom corner")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle1_right, paddle1_bottom, paddle1_right, paddle1_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle1 side - bottom corner")
		ball.position = intersection
		ball.position.x += ball.size / 2
		ball.direction.x *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, ball_right, ball.position.y, ball_next_step_right.x, ball_next_step_right.y):
		logging.info("Paddle2 side")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction = calculate_ball_direction_after_collision(paddle2, ball)
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_top, paddle2_right, paddle2_top, ball.position.x, ball_bottom, ball_next_step_down.x, ball_next_step_down.y):
		logging.info("Paddle2 top")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_right, paddle2_bottom, ball.position.x, ball_top, ball_next_step_up.x, ball_next_step_up.y):
		logging.info("Paddle2 bottom")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_top, paddle2_right, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 top - top corner")
		ball.position = intersection
		ball.position.y -= ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 side - top corner")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction.x *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_right, paddle2_bottom, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 bottom - bottom corner")
		ball.position = intersection
		ball.position.y += ball.size / 2
		ball.direction.y *= -1
		ball.speed += 0.1
	elif intersection := get_line_intersection(paddle2_left, paddle2_bottom, paddle2_left, paddle2_top, collision_point.x, collision_point.y, ball_collision_next.x, ball_collision_next.y):
		logging.info("Paddle2 side - bottom corner")
		ball.position = intersection
		ball.position.x -= ball.size / 2
		ball.direction.x *= -1
		ball.speed += 0.1
	return ball