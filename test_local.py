from nose.tools import assert_equal
from .config_local import config
import json
import requests
import logging

# test_online 的拷贝
# 只改了一下 config 源

class test_backend:

    def cleardb(self):
        logging.info("clear databases")
        # 请空数据库
        r = requests.delete(self.records_url)
        assert_equal(r.status_code == 200, True, "delete records failed")

        r = requests.delete(self.videos_url)
        assert_equal(r.status_code == 200, True, "delete videos failed")

    def setup(self):
        self.base_url = config["domin"] + ":" + config["port"] + "/api/"
        logging.info(self.base_url)

        self.records_url = self.base_url + "records" 
        self.videos_url = self.base_url + "videos" 
        self.post_all_records_url = self.records_url + "/all"
        self.get_all_videos_url = self.videos_url + "/all"
        self.event_list = ["longEnough", "like", "coin", "favorite", "share"] # 目前支持汇报的事件列表

        # 保存records
        r = requests.get(self.records_url, 
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "get records failed")
        records = json.loads(r.content)
        with open("records_save.json", "w") as f:
            json.dump(records, f)

        # 保存videos，videos需要转换下play
        r = requests.get(self.videos_url+"/all", 
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "get videos failed")
        videos = json.loads(r.content)
        with open("videos_save.json", "w") as f:
            json.dump(videos, f)


    # 测试服务有没有挂掉
    def test_avaliable(self):
        self.cleardb()

        r = requests.get(self.records_url, 
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        assert_equal(r.status_code, 200, "service failed")

    # 测试post一条记录
    def test_records_post(self):
        self.cleardb()

        with open("json/post_records.json","r") as f:
            j = json.load(f)

        uid = j["uid"]

        # 获取目前records数目，在线上环境有必要，线下没必要，因为测试时可能有数据进来
        r_get = requests.get(self.records_url+"?uid={}".format(uid), 
                         headers={"content-type": "application/json"})
        records_before = len(json.loads(r_get.content))
        logging.info("user {} has {} records before post records".format(uid, records_before))

        # 获取目前 videos 数目
        r_get = requests.get(self.videos_url+"/all", 
                         headers={"content-type": "application/json"})
        videos_before = len(json.loads(r_get.content))
        logging.info("videos table has {} videos before post records".format(videos_before))

        # post 一条新 record
        r = requests.post(self.records_url, json=j,
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        assert_equal(r.status_code, 200, "status code is not 200")

        # 获取目前 records 数目
        r_get = requests.get(self.records_url+"?uid={}".format(uid), 
                         headers={"content-type": "application/json"})
        records_after = len(json.loads(r_get.content))
        logging.info("user {} has {} records after post records".format(uid, records_after))

        # 获取post 之后 videos 数目
        r_get = requests.get(self.videos_url+"/all", 
                         headers={"content-type": "application/json"})
        videos_after = len(json.loads(r_get.content)) 
        logging.info("videos table has {} videos before post records".format(videos_after))

        # 验证确实插入了一条记录
        assert_equal(records_after - records_before, 1 , "post method failed")

        # 验证videos表中也新增了视频
        assert_equal(videos_after - videos_before, 1, "insert new video into videos table failed")

    # 测试 post videos 接口，一次post进来大量数据
    # 现在没办法通过get 获取videos的信息
    def test_videos_post(self):
        self.cleardb()
        
        with open("json/post_videos.json","r") as f:
            j = json.load(f)
        size_post = len(j["content"])
        
        r_get = requests.get(self.videos_url+"/all", 
                         headers={"content-type": "application/json"})
        videos_before = len(json.loads(r_get.content))
        logging.info("there are {} videos before post videos".format(videos_before))

        r = requests.post(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        assert_equal(r.status_code, 200, "status code is not 200")

        r_get = requests.get(self.videos_url+"/all", 
                         headers={"content-type": "application/json"})
        videos_after = len(json.loads(r_get.content))
        logging.info("there are {} videos after post videos".format(videos_after))

        #验证确实插入了多条videos
        assert_equal(videos_after - videos_before, size_post , "post method failed")

    #简单测试一下get
    # def test_records_get(self):
    #     records_url = self.base_url + "records"
    #     with open("json/post_records.json","r") as f:
    #         j = json.load(f)
    #     uid = j["uid"] 

    #     url = records_url + "?uid={}".format(uid)
    #     logging.info("url:{}".format(url))

    #     r = requests.get(url, 
    #                      headers={"content-type": "application/json"})
    #     logging.info(r.status_code)
    #     logging.info("records database have {} items".format(len(json.loads(r.content))))
    #     assert_equal(r.status_code == 200 and len(json.loads(r.content)) >= 0, True, "get records failed")


    # 测试删除接口是否正常
    def test_records_delete(self):
        self.cleardb()

        # 先post
        with open("json/post_records.json","r") as f:
            j = json.load(f)
        
        # 测试 /delete 
        r = requests.post(self.records_url, json=j,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code == 200, True, "delete records failed")
                         
        r = requests.delete(self.records_url)
        logging.info(r.status_code)
        r_get = requests.get(self.records_url, 
                         headers={"content-type": "application/json"})

        logging.info("records database have {} items after delete".format(len(json.loads(r_get.content))))
        assert_equal(r.status_code == 200 and len(json.loads(r_get.content)) == 0, True, "delete records failed")


        # 测试 /delete?uid=xxx
        r = requests.post(self.records_url, json=j,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code == 200, True, "delete records failed")

        uid = j["uid"] 
        url = self.records_url + "?uid={}".format(uid)
        logging.info("url:{}".format(url))

        r = requests.delete(url)
        logging.info(r.status_code)
        r_get = requests.get(url, 
                         headers={"content-type": "application/json"})

        #logging.info("records database have {} items after delete".format(len(json.loads(r_get.content))))
        assert_equal(r.status_code == 200 and len(json.loads(r_get.content)) == 0 , True, "delete records failed")

    # 与 test_records_delete 基本相同
    def test_delete_videos(self):
        self.cleardb()

        # 先post
        with open("json/post_videos.json","r") as f:
            j = json.load(f)
        
        # 测试 /delete 
        r = requests.post(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code == 200, True, "delete videos failed")
                         
        r = requests.delete(self.videos_url)
        logging.info(r.status_code)
        r_get = requests.get(self.get_all_videos_url, 
                         headers={"content-type": "application/json"})

        #logging.info("videos database have {} items after delete".format(len(json.loads(r_get.content)["content"])))
        assert_equal(r.status_code == 200 and len(json.loads(r_get.content)) == 0, True, "delete videos failed")

    # def test_videos_get(self):
    #     """
    #     验证get next videos接口通
    #     """
    #     cleardb()
    #     assert_equal(1,1)

    # def test_videos_event(self):
    #     """
    #     验证post event时，分数会相应改变
    #     """
    #     # 同一个视频
    #     assert_equal(1,1)

    def test_videos_low_score(self):
        """
        一个视频被多次推荐但是没有正反馈时不会再被推荐
        或者验证所有视频分数都为10以下时选不出视频
        """
        # 首先 post 一个视频，然后不断 get
        # 最后 将 get 不到视频
        self.cleardb()

        with open("json/post_videos_low_score.json", "r") as f:
            j = json.load(f)
        r = requests.post(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
        logging.info(r.status_code)
        assert_equal(r.status_code, 200, "status code is not 200")

        for i in range(6):
            r = requests.get(self.videos_url, headers={"content-type": "application/json"})
            logging.info(r.status_code)
            assert_equal(r.status_code, 200, "status code is not 200")

        r = requests.get(self.videos_url, headers={"content-type": "application/json"})
        logging.info(r.status_code) 
        assert_equal(r.status_code, 200, "status code is not 200")
        
        # 如果无视频，返回 "null"
        assert_equal(r.text == "null", True, "low score videos are not handled correctly in recommendation chain")

    def test_videos_high_score(self):
        """
        验证正面反馈会增大推荐的概率...比较难验证
        先验证正面反馈会加分
        """
        self.cleardb()
        # 先 post 一条 video
        with open("json/post_videos_high_score.json", "r") as f:
            j = json.load(f)
        r = requests.post(self.videos_url, json=j,
                         headers={"content-type": "application/json"})

        r = requests.get(self.get_all_videos_url, headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "status code is not 200")
        origin_score = json.loads(r.content)[0]["score"]
        
        with open("json/patch_videos_high_score.json", "r") as f:
            j = json.load(f)
                        
        # 各种事件都汇报一遍
        for event in self.event_list:
            j["event"] = event 
            r = requests.patch(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
            assert_equal(r.status_code, 200, "status code is not 200")
            r = requests.get(self.get_all_videos_url, headers={"content-type": "application/json"})
            assert_equal(r.status_code, 200, "status code is not 200")
            assert_equal(len(json.loads(r.content)) != 0, True, "no videos!")
            score = json.loads(r.content)[0]["score"]
            assert_equal(score > origin_score, True, "report event and add score failed")
            origin_score = score

    def test_videos_high_play(self):
        """
        验证播放量100以上停止推送视频
        """
        self.cleardb()
        with open("json/post_videos_high_play.json", "r") as f:
            j = json.load(f)
        r = requests.post(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "status code is not 200")
        
        with open("json/patch_videos_high_play.json", "r") as f:
            j = json.load(f)
        r = requests.patch(self.videos_url, json=j,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "status code is not 200")

        # 现在应当 get 不到视频
        r = requests.get(self.videos_url, headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "status code is not 200")

        assert_equal(r.text == "null", True, "high play videos are not handled correctly in recommendation chain")


    # 先清空数据库，再恢复数据
    def teardown(self):
        self.cleardb()

        # 恢复 records
        with open("records_save.json", "r") as f:
            records = json.load(f)
        req = {}
        req["content"] = records
        r = requests.post(self.post_all_records_url, json=req,
                         headers={"content-type": "application/json"})
        assert_equal(r.status_code, 200, "restore records failed")

        # 恢复 videos
        with open("videos_save.json", "r") as f:
            videos = json.load(f)
        req = {}
        req["content"] = videos
        if videos != []:
            # 做转换，将play转为int型
            for video in req["content"]:
                video["play"] = int(video["play"])

            r = requests.post(self.videos_url, json=req,
                            headers={"content-type": "application/json"})
            assert_equal(r.status_code, 200, "restore videos failed")