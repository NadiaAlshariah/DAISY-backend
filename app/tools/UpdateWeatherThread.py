from apscheduler.schedulers.background import BackgroundScheduler
from app.database import mongo
from datetime import datetime
from app.services.BlockService import BlockService


def update_weather_for_all_lands():
    lands = list(mongo.db.lands.find({}))

    for land in lands:
        land_id = land["_id"]

        try:
            blocks = BlockService.get_blocks_by_land_id(str(land_id))
            for block in blocks:
                BlockService.run_weather_and_predictions_for_block(block)

        except Exception as e:
            print(f"❌ Failed to process land {land_id}: {e}")


def start_weather_scheduler(app):
    scheduler = BackgroundScheduler()

    @scheduler.scheduled_job('cron', hour=12, minute=0)
    def scheduled_job():
        with app.app_context():
            update_weather_for_all_lands()

    scheduler.start()
    print("sch_started")
