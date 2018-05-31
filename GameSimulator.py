import itertools as it
import skimage.color
import skimage.transform
import numpy as np
import tetris_fun

class GameSimulator:
    def __init__(self, frame_repeat=4, resolution=(10, 20, 1)):
        self.game = None
        self.frame_repeat = frame_repeat
        self.resolution = resolution
        self.actions = []
        self.rewards = 0.0
        self.last_action = 0
        
    def initialize(self):
        print("Initializing doom...")
        self.game = GameState()
        self.game.reinit()
        n = 6
#        self.actions = [list(a) for a in it.product([0, 1], repeat=n)]
        self.actions = []
        for i in range(n):
            ac = [0]*n
            ac[i] = 1
            self.actions.append(ac)
        print("self.actions---------------------------------")
        print(self.actions)
        print(type(self.actions))
    
    # 对游戏图像进行处理，后期可能放到GameSimulator中
    def __preprocess(self, img):
        img = skimage.transform.resize(img, self.resolution, mode='constant')
        img = img.astype(np.float32)
        return img
    
    def get_state(self, preprocess=True):
        # 获取当前游戏的画面，游戏结束则获得空
        if not self.game.isValidPosition():
            return None
        img = self.game.get_state()
        #img = img.reshape([self.screen_height, self.screen_width])
        # 如果进行预处理
        if preprocess: img = self.__preprocess(img)

        # put action into 4th channel
        height = self.resolution[0]
        width = self.resolution[1]
        channel = self.resolution[2]
        img = img.reshape([height*width*channel])
        img = list(img)
        action_space = height*width
        action_len = action_space//len(self.actions)
        action_remain = action_space%len(self.actions)
        img = img + ([0]*action_remain)
        for i in range(len(self.actions)):
            if(i==self.last_action):
                img = img + ([1]*action_len)
            else:
                img = img + ([0]*action_len)
        img_with_action = np.array(img)
        img_with_action = img_with_action.reshape([height,width,channel+1])

        return img_with_action
    
    def get_action_size(self):
        # 获取动作数目
        return 6
    
    def make_action(self, action):
        now_action = self.actions[action]
        #print('make action ', now_action)
        _, reward, _, _ = self.game.frame_step(now_action)
        reward = reward / 10
        new_state = self.get_state()
        done = self.is_episode_finished()
        self.rewards += reward
        self.last_action = action
        return new_state, reward, done
    
    def is_episode_finished(self):
        # 判断游戏是否终止
        return not self.game.isValidPosition()
    
    def reset(self):
        # 重新开始游戏
        self.game.reinit()
        self.rewards = 0.0
        
    def get_total_reward(self):
        return self.rewards
