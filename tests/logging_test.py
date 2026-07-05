from backend_server.block_app.services.log_service import logger
import logging

def test_logs_message(caplog):

    with caplog.at_level(logging.INFO):
        pass