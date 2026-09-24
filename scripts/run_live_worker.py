from app.services.live_worker import LiveSyncWorker


def main():
    worker = LiveSyncWorker()

    try:
        worker.run_forever()
    except KeyboardInterrupt:
        print("Stopping live sync worker...")
        worker.stop()
        worker.close()


if __name__ == "__main__":
    main()