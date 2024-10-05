import logging
import os

import seqlog

SERVER_URL = os.getenv("SEQ_URL", default="http://localhost:5341/")


def seq_logger_init():
    seqlog.log_to_seq(
        server_url=SERVER_URL,
        level=logging.INFO,
        batch_size=10,
        auto_flush_timeout=1,
        override_root_logger=True
    )

    logging.info('seq_service:: seq initialized')
