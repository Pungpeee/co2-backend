from django.core.management import BaseCommand

from news_update.models import NewsUpdate


class Command(BaseCommand):
    help = 'News Update Migrate desc to short_desc'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS(self.help))
        for news_update in NewsUpdate.objects.all():
            if not news_update.short_desc:
                self.stdout.write(self.style.SUCCESS('Migrate news_update_id: %s' % news_update.id))
                news_update.clean_desc()

        self.stdout.write(self.style.SUCCESS('Successfully.'))
