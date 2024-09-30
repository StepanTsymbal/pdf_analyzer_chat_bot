import logging
import seqlog

SERVER_URL = "http://localhost:5341/"


def seq_logger_init():
    seqlog.log_to_seq(
        server_url=SERVER_URL,
        level=logging.NOTSET,
        batch_size=10,
        auto_flush_timeout=1,
        override_root_logger=True
    )

    logging.info('seq_service:: seq initialized')
