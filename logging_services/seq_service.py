import logging
import seqlog


def seq_logger_init():
    seqlog.log_to_seq(
        server_url="http://localhost:5341/",
        # api_key="RK**********sttQJA9F",
        level=logging.NOTSET,
        batch_size=10,
        auto_flush_timeout=1,
        override_root_logger=True
    )

    logging.info('seq_service:: seq initialized')
