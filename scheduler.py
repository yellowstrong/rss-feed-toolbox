import threading

from apscheduler.executors.pool import ThreadPoolExecutor
from apscheduler.schedulers.background import BackgroundScheduler

from app.config.app_config import app_config
from app.constant.time import ChinaTimeZone
from app.jobs import subscribe, transfer
from app.types.schedule import ScheduleInfo
from app.helper.logger_helper import logger
from app.utils.singleton import Singleton
from app.utils.time import time_difference


class Scheduler(metaclass=Singleton):
    _scheduler: BackgroundScheduler | None = None
    _event = threading.Event()
    _lock = threading.Lock()
    _jobs = {}

    def __init__(self):
        self.init()

    def init(self):
        self._jobs = {
            'subscribe': {
                'name': '订阅RSS刷新',
                'func': subscribe.SubscribeJob().refresh,
                'running': False
            },
            'transfer': {
                'name': '文件转移服务',
                'func': transfer.transfer,
                'running': False
            }
        }
        self.stop()

        self._scheduler = BackgroundScheduler(
            timezone=ChinaTimeZone,
            executors={
                'default': ThreadPoolExecutor(100)
            }
        )

        if app_config.SUBSCRIBE_INTERVAL and str(app_config.SUBSCRIBE_INTERVAL).isdigit():
            self._scheduler.add_job(
                self.start,
                'interval',
                id='subscribe',
                name='订阅RSS刷新',
                minutes=int(app_config.SUBSCRIBE_INTERVAL),
                kwargs={
                    'job_id': 'subscribe'
                }
            )

        self._scheduler.start()

        self._scheduler.print_jobs()

    def start(self, job_id: str, *args, **kwargs):
        with self._lock:
            job = self._jobs.get(job_id)
            if not job:
                return
            job_name = job.get('name')
            if job.get("running"):
                logger.warning(f"定时任务 {job_id} - {job_name} 正在运行 ...")
                return
            self._jobs[job_id]["running"] = True
        try:
            if not kwargs:
                kwargs = job.get("kwargs") or {}
            job["func"](*args, **kwargs)
        except Exception as e:
            logger.error(f"定时任务 {job_name} 执行失败: {str(e)}")
        with self._lock:
            try:
                self._jobs[job_id]["running"] = False
            except KeyError:
                pass

    def list(self) -> list[ScheduleInfo]:
        if not self._scheduler:
            return []
        with self._lock:
            schedulers = []
            added = []
            jobs = self._scheduler.get_jobs()
            jobs.sort(key=lambda x: x.next_run_time)
            for job_id, service in self._jobs.items():
                name = service.get("name")
                if service.get("running") and name:
                    if name not in added:
                        added.append(name)
                    schedulers.append(ScheduleInfo(
                        id=job_id,
                        name=name,
                        status="正在运行",
                    ))
            for job in jobs:
                if job.name not in added:
                    added.append(job.name)
                else:
                    continue
                job_id = job.id
                service = self._jobs.get(job_id)
                if not service:
                    continue
                status = "正在运行" if service.get("running") else "等待"
                next_run = time_difference(job.next_run_time)
                schedulers.append(ScheduleInfo(
                    id=job_id,
                    name=job.name,
                    status=status,
                    next_run=next_run
                ))
            return schedulers

    def stop(self):
        try:
            if self._scheduler:
                logger.info('正在停止定时任务...')
                self._event.set()
                self._scheduler.remove_all_jobs()
                if self._scheduler.running:
                    self._scheduler.shutdown()
                self._scheduler = None
                logger.info('定时任务停止完成')
        except Exception as e:
            logger.error(f'停止定时任务失败: {str(e)}')
