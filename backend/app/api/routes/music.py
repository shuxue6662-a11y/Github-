"""
音乐生成 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import io
import base64
import time

from app.models.schemas import (
    MusicGenerateRequest,
    MusicResponse,
    StylesResponse,
    StyleInfo,
)
from app.models.enums import MusicStyle
from app.services.github_service import GitHubService
from app.services.commit_analyzer import CommitAnalyzer
from app.services.music_generator import MusicGenerator
from app.services.midi_builder import MidiBuilder
from app.api.deps import get_github_service
from app.utils.helpers import parse_repo_url
from app.core.instruments import STYLE_CONFIGS


router = APIRouter()


# 风格描述
STYLE_DESCRIPTIONS = {
    MusicStyle.ELECTRONIC: "Modern electronic beats with synths",
    MusicStyle.CLASSICAL: "Elegant piano and orchestral sounds",
    MusicStyle.ROCK: "Energetic guitars and driving drums",
    MusicStyle.JAZZ: "Smooth jazz with swing rhythm",
    MusicStyle.AMBIENT: "Ethereal pads and atmospheric textures",
    MusicStyle.CHIPTUNE: "Retro 8-bit video game sounds",
    MusicStyle.LOFI: "Chill lo-fi hip hop vibes",
    MusicStyle.ORCHESTRAL: "Epic orchestral arrangements",
}

STYLE_EMOJIS = {
    MusicStyle.ELECTRONIC: "🎹",
    MusicStyle.CLASSICAL: "🎻",
    MusicStyle.ROCK: "🎸",
    MusicStyle.JAZZ: "🎷",
    MusicStyle.AMBIENT: "🌊",
    MusicStyle.CHIPTUNE: "👾",
    MusicStyle.LOFI: "☕",
    MusicStyle.ORCHESTRAL: "🎼",
}


@router.post("/generate", response_model=MusicResponse)
async def generate_music(
    request: MusicGenerateRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    根据 GitHub 仓库生成音乐
    
    将仓库的 commit 历史转换为音乐数据，可用于前端播放或下载 MIDI。
    
    映射规则：
    - **Commit 类型** → 乐器和音色
    - **修改量** → 音符力度和密度
    - **时间分布** → 节奏变化
    - **贡献者** → 和声层
    """
    start_time = time.time()
    
    try:
        # 1. 解析并获取 commits
        owner, repo = parse_repo_url(request.repo_url)
        
        commits = await github_service.get_commits(
            owner, repo,
            branch=request.branch,
            max_count=request.max_commits
        )
        
        if not commits:
            raise HTTPException(
                status_code=404,
                detail=f"No commits found in {owner}/{repo}"
            )
        
        # 2. 分析 commits
        analyzer = CommitAnalyzer()
        analysis = analyzer.analyze(commits)
        
        # 3. 生成音乐数据
        generator = MusicGenerator(
            style=request.style,
            bpm=request.bpm,
            scale=request.scale,
            include_drums=request.include_drums,
            include_bass=request.include_bass,
            include_chords=request.include_chords,
            melody_complexity=request.melody_complexity,
        )
        music_data = generator.generate(analysis)
        
        # 4. 生成 MIDI 文件
        midi_builder = MidiBuilder()
        midi_bytes = midi_builder.build(music_data)
        midi_base64 = base64.b64encode(midi_bytes).decode('utf-8')
        
        # 计算统计
        total_notes = sum(len(track.notes) for track in music_data.tracks)
        generation_time = (time.time() - start_time) * 1000
        
        return MusicResponse(
            success=True,
            repo_name=f"{owner}/{repo}",
            style=request.style,
            bpm=music_data.bpm,
            scale=str(request.scale.value),
            duration=music_data.total_duration,
            total_tracks=len(music_data.tracks),
            total_notes=total_notes,
            music_data=music_data,
            midi_base64=midi_base64,
            commits_processed=len(commits),
            generation_time_ms=round(generation_time, 2),
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate music: {str(e)}"
        )


@router.post("/download-midi")
async def download_midi(
    request: MusicGenerateRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    下载 MIDI 文件
    
    直接返回可下载的 MIDI 文件。
    """
    try:
        # 复用生成逻辑
        owner, repo = parse_repo_url(request.repo_url)
        commits = await github_service.get_commits(
            owner, repo, 
            branch=request.branch,
            max_count=request.max_commits
        )
        
        if not commits:
            raise HTTPException(status_code=404, detail="No commits found")
        
        analyzer = CommitAnalyzer()
        analysis = analyzer.analyze(commits)
        
        generator = MusicGenerator(
            style=request.style, 
            bpm=request.bpm,
            scale=request.scale,
        )
        music_data = generator.generate(analysis)
        
        midi_builder = MidiBuilder()
        midi_bytes = midi_builder.build(music_data)
        
        # 生成文件名
        safe_name = repo.replace('/', '_').replace(' ', '_')
        filename = f"{safe_name}_rhythm.mid"
        
        return StreamingResponse(
            io.BytesIO(midi_bytes),
            media_type="audio/midi",
            headers={
                "Content-Disposition": f'attachment; filename="{filename}"'
            }
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles", response_model=StylesResponse)
async def get_available_styles():
    """
    获取所有可用的音乐风格
    
    返回每种风格的信息，包括名称、描述、推荐 BPM 范围等。
    """
    styles = []
    
    for style in MusicStyle:
        config = STYLE_CONFIGS.get(style, {})
        bpm_range = config.get("bpm_range", (100, 140))
        
        styles.append(StyleInfo(
            id=style.value,
            name=style.name.replace('_', ' ').title(),
            description=STYLE_DESCRIPTIONS.get(style, ""),
            emoji=STYLE_EMOJIS.get(style, "🎵"),
            bpm_range=bpm_range,
        ))
    
    return StylesResponse(styles=styles)


@router.get("/scales")
async def get_available_scales():
    """
    获取所有可用的音阶
    """
    from app.models.enums import ScaleType
    
    return {
        "scales": [
            {
                "id": scale.value,
                "name": scale.name.replace('_', ' ').title(),
            }
            for scale in ScaleType
        ]
    }