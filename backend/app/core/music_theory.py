"""
高级乐理工具
"""
from typing import List, Tuple, Optional
import random

from app.core.scales import (
    get_scale_notes, 
    get_chord_notes, 
    get_scale_chord,
    CHORD_PROGRESSIONS,
    ScaleType,
)


class MelodyGenerator:
    """旋律生成器"""
    
    def __init__(self, scale: ScaleType, complexity: float = 0.5):
        """
        Args:
            scale: 音阶
            complexity: 复杂度 0-1
        """
        self.scale = scale
        self.complexity = complexity
        self.scale_notes = get_scale_notes(scale, octaves=2)
        self.last_note_index = len(self.scale_notes) // 2
    
    def generate_note(
        self,
        energy: float = 0.5,
        direction_hint: int = 0,
    ) -> int:
        """
        生成下一个音符
        
        Args:
            energy: 能量级别 0-1，影响音符跳跃
            direction_hint: -1 向下, 0 随机, 1 向上
        
        Returns:
            MIDI 音高
        """
        if not self.scale_notes:
            return 60
        
        # 计算跳跃范围
        max_jump = int(1 + energy * 4 + self.complexity * 3)
        
        # 确定方向
        if direction_hint == 0:
            direction = random.choice([-1, 1])
        else:
            direction = direction_hint
        
        # 计算新索引
        jump = random.randint(1, max_jump)
        new_index = self.last_note_index + (direction * jump)
        
        # 边界处理
        new_index = max(0, min(len(self.scale_notes) - 1, new_index))
        
        # 偶尔保持不变
        if random.random() < 0.15:
            new_index = self.last_note_index
        
        self.last_note_index = new_index
        return self.scale_notes[new_index]
    
    def generate_phrase(
        self,
        length: int,
        start_energy: float = 0.3,
        end_energy: float = 0.3,
        peak_position: float = 0.6,
    ) -> List[int]:
        """
        生成一个乐句
        
        Args:
            length: 音符数量
            start_energy: 起始能量
            end_energy: 结束能量
            peak_position: 高潮位置 (0-1)
        
        Returns:
            音符列表
        """
        notes = []
        
        for i in range(length):
            position = i / max(1, length - 1)
            
            # 计算当前位置的能量（抛物线形状）
            if position < peak_position:
                energy = start_energy + (1.0 - start_energy) * (position / peak_position)
            else:
                remaining = (position - peak_position) / (1.0 - peak_position)
                energy = 1.0 - (1.0 - end_energy) * remaining
            
            # 方向暗示：结尾倾向向下
            direction = 0
            if position > 0.8:
                direction = -1
            
            note = self.generate_note(energy, direction)
            notes.append(note)
        
        return notes
    
    def reset(self):
        """重置到中间位置"""
        self.last_note_index = len(self.scale_notes) // 2


class ChordProgressionGenerator:
    """和弦进行生成器"""
    
    def __init__(self, scale: ScaleType, progression_type: str = "pop"):
        self.scale = scale
        self.progression = CHORD_PROGRESSIONS.get(
            progression_type, 
            CHORD_PROGRESSIONS["pop"]
        )
        self.current_index = 0
    
    def get_next_chord(self, use_seventh: bool = False) -> Tuple[int, str, List[int]]:
        """
        获取下一个和弦
        
        Returns:
            (根音, 和弦类型, 音符列表)
        """
        degree = self.progression[self.current_index]
        root, chord_type = get_scale_chord(self.scale, degree, seventh=use_seventh)
        notes = get_chord_notes(root, chord_type)
        
        self.current_index = (self.current_index + 1) % len(self.progression)
        
        return (root, chord_type, notes)
    
    def get_full_progression(
        self,
        use_seventh: bool = False,
    ) -> List[Tuple[int, str, List[int]]]:
        """获取完整的和弦进行"""
        result = []
        for degree in self.progression:
            root, chord_type = get_scale_chord(self.scale, degree, seventh=use_seventh)
            notes = get_chord_notes(root, chord_type)
            result.append((root, chord_type, notes))
        return result
    
    def reset(self):
        """重置到开头"""
        self.current_index = 0


class VoiceLeading:
    """声部进行优化"""
    
    @staticmethod
    def smooth_chord_transition(
        prev_chord: List[int],
        next_chord: List[int],
    ) -> List[int]:
        """
        优化和弦连接，使用最近的转位
        
        Args:
            prev_chord: 前一个和弦音符
            next_chord: 下一个和弦音符
        
        Returns:
            优化后的下一个和弦
        """
        if not prev_chord:
            return next_chord
        
        # 生成所有可能的转位
        inversions = []
        for i in range(len(next_chord)):
            inversion = []
            for j, note in enumerate(next_chord):
                # 调整八度
                adjusted = note
                if j < i:
                    adjusted += 12
                inversion.append(adjusted)
            inversions.append(sorted(inversion))
        
        # 找到与前一个和弦最接近的转位
        prev_center = sum(prev_chord) / len(prev_chord)
        
        best_inversion = next_chord
        best_distance = float('inf')
        
        for inv in inversions:
            center = sum(inv) / len(inv)
            distance = abs(center - prev_center)
            if distance < best_distance:
                best_distance = distance
                best_inversion = inv
        
        return best_inversion


def calculate_velocity_curve(
    position: float,
    base_velocity: int,
    phrase_length: int,
    accent_beats: List[int] = None,
) -> int:
    """
    计算动态力度曲线
    
    Args:
        position: 当前位置 (0-1)
        base_velocity: 基础力度
        phrase_length: 乐句长度
        accent_beats: 重音位置
    
    Returns:
        力度值 (0-127)
    """
    velocity = base_velocity
    
    # 乐句形状：中间稍强
    phrase_curve = 1.0 + 0.15 * (1.0 - abs(position - 0.5) * 2)
    velocity = int(velocity * phrase_curve)
    
    # 添加微小随机变化
    velocity += random.randint(-5, 5)
    
    return max(1, min(127, velocity))


def humanize_timing(
    time: float,
    amount: float = 0.02,
) -> float:
    """
    添加人性化的时间偏移
    
    Args:
        time: 原始时间
        amount: 偏移量（拍）
    
    Returns:
        偏移后的时间
    """
    offset = random.uniform(-amount, amount)
    return max(0, time + offset)


def humanize_velocity(
    velocity: int,
    amount: int = 10,
) -> int:
    """
    添加人性化的力度变化
    """
    offset = random.randint(-amount, amount)
    return max(1, min(127, velocity + offset))