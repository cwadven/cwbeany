from django.core.management.base import BaseCommand
from django_seed import Seed
from board.models import *
from accounts.models import *
from control.models import *
import random


class Command(BaseCommand):
    def add_arguments(self, parser):
        parser.add_argument("--board-group-creation-number", default=0)
        parser.add_argument("--board-creation-number", default=0)
        parser.add_argument("--post-creation-number", default=0)
        parser.add_argument("--reply-creation-number", default=0)
        parser.add_argument("--rereply-creation-number", default=0)
        parser.add_argument("--tag-creation-number", default=0)
        # parser.add_argument("--tag-post-creation-number", default=0)
        parser.add_argument("--announce-creation-number", default=0)

    def handle(self, *args, **kwargs):
        board_group_creation_number = int(kwargs.get("board_group_creation_number"))
        board_creation_number = int(kwargs.get("board_creation_number"))
        post_creation_number = int(kwargs.get("post_creation_number"))
        reply_creation_number = int(kwargs.get("reply_creation_number"))
        rereply_creation_number = int(kwargs.get("rereply_creation_number"))
        tag_creation_number = int(kwargs.get("tag_creation_number"))
        # tag_post_creation_number = int(kwargs.get("tag_post_creation_number"))
        announce_creation_number = int(kwargs.get("announce_creation_number"))
        seeder = Seed.seeder()
        if board_group_creation_number:
            # Add BoardGroups
            seeder.add_entity(
                BoardGroup,
                board_group_creation_number,
                {
                    'group_name': lambda x: seeder.faker.domain_word(),
                }
            )

        # Add Boards
        if board_creation_number:
            seeder.add_entity(
                Board,
                board_creation_number,
                {
                    'board_group': lambda x: random.choice(BoardGroup.objects.all()),
                    'url': lambda x: seeder.faker.domain_word(),
                    'name': lambda x: seeder.faker.domain_word(),
                    'board_img': None,
                    'attribute': 0,
                }
            )

        if post_creation_number:
            # Add Posts
            seeder.add_entity(
                Post,
                post_creation_number,
                {
                    'def_tag': None,
                    'post_img': None,
                    'board': lambda x: random.choice(Board.objects.all()),
                    'author': lambda x: random.choice(User.objects.all()),
                }
            )

        # Add Replys
        if reply_creation_number:
            seeder.add_entity(
                Reply,
                reply_creation_number,
                {
                    'post': lambda x: random.choice(Post.objects.all()),
                    'author': lambda x: random.choice(User.objects.all()),
                }
            )

        # Add Rereplys
        if rereply_creation_number:
            seeder.add_entity(
                Rereply,
                rereply_creation_number,
                {
                    'post': lambda x: random.choice(Post.objects.all()),
                    'reply': lambda x: random.choice(Reply.objects.all()),
                    'author': lambda x: random.choice(User.objects.all()),
                }
            )

        # Add Tags
        if tag_creation_number:
            seeder.add_entity(
                Tag,
                tag_creation_number,
                {
                    'tag_name': lambda x: seeder.faker.user_name(),
                }
            )

        # Add TagPosts
        # if tag_post_creation_number:
        #     for i in range(tag_post_creation_number):
        #         tag = Tag.objects.order_by('?')[0]
        #         post = Post.objects.exclude(tag_set=tag).order_by('?')[0]
        #         if post:
        #             post.tag_set.add(tag)

        # Add Announces
        if announce_creation_number:
            seeder.add_entity(
                Announce,
                announce_creation_number,
            )

        # Execute
        seeder.execute()
