import random

class RandomUniqueSelector:
    def __init__(self, items):
        self.items = items[:]  # 原始列表的副本
        self.reset()

    def reset(self):
        self.current_items = self.items[:]
        random.shuffle(self.current_items)  # 打乱顺序以确保随机性
        self.index = 0

    def get_next(self):
        if self.index >= len(self.current_items):
            self.reset()  # 当所有元素都被选过后，重置状态
        result = self.current_items[self.index]
        self.index += 1
        return result