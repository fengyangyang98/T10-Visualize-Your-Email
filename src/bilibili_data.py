from bilibili_api import user
from bilibili_api import video
import time
import datetime

class bilibili_data:
    def get_user_videos_record(uid):
        record_gen = user.get_videos(uid = uid, order = 'pubdate')

        end_time = datetime.datetime.now()
        start_time = end_time - datetime.timedelta(days = 365)

        for record in record_gen:
            video_no = record['bvid']
            video_info = video.get_video_info(bvid = video_no)
            print(time.ctime(video_info['ctime']))