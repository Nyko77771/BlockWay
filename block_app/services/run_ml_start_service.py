from block_app.services.start_service import StartService

def start_scheduler():
    scheduler = StartService()
    scheduler.make_scheduler()
    return scheduler