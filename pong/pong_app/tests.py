from django.test import TestCase
from .models import Player, PlayerMatch, Match  # Import the Match model

class PlayerMatchTestCase(TestCase):
    def setUp(self):
        # Create mock players with unique emails
        self.player_left = Player.objects.create(username='left_player', wins=0, losses=0)
        self.player_right = Player.objects.create(username='right_player', wins=0, losses=0)
        self.player_up = Player.objects.create(username='up_player', wins=0, losses=0)
        self.player_down = Player.objects.create(username='down_player', wins=0, losses=0)
        
        # Create a Match instance
        self.match = Match.objects.create(
            game=Match.Game.PONG.value,
            tournament=None,  # Assuming no tournament for simplicity
            round=1,
            state=Match.State.UNPLAYED.value
        )

    def test_player_match(self):
        # Simulate the function call
        player_left_db = Player.objects.get(id=self.player_left.id)
        player_right_db = Player.objects.get(id=self.player_right.id)
        player_up_db = Player.objects.get(id=self.player_up.id)
        player_down_db = Player.objects.get(id=self.player_down.id)
        
        player_match_left, created = PlayerMatch.objects.get_or_create(
            match_id=self.match,
            player_id=player_left_db
        )
        player_match_right, created = PlayerMatch.objects.get_or_create(
            match_id=self.match,
            player_id=player_right_db
        )
        player_match_up, created = PlayerMatch.objects.get_or_create(
            match_id=self.match,
            player_id=player_up_db
        )
        player_match_down, created = PlayerMatch.objects.get_or_create(
            match_id=self.match,
            player_id=player_down_db
        )
        
        winner = 'left'  # Simulate a winner
        
        match winner:
            case 'left':
                player_match_left.score = 1
                player_match_left.won = True
                player_match_right.score = 0
                player_match_right.won = False
                player_match_up.score = 0
                player_match_up.won = False
                player_match_down.score = 0
                player_match_down.won = False
                player_left_db.wins += 1
                player_right_db.losses += 1
                player_up_db.losses += 1
                player_down_db.losses += 1
                result = player_left_db.username + ' is the winner'
        
        # Save changes
        player_match_left.save()
        player_match_right.save()
        player_match_up.save()
        player_match_down.save()
        player_left_db.save()
        player_right_db.save()
        player_up_db.save()
        player_down_db.save()
        
        # Assertions
        self.assertEqual(player_match_left.score, 1)
        self.assertTrue(player_match_left.won)
        self.assertEqual(player_match_right.score, 0)
        self.assertFalse(player_match_right.won)
        self.assertEqual(player_left_db.wins, 1)
        self.assertEqual(player_right_db.losses, 1)
        self.assertEqual(result, 'left_player is the winner')