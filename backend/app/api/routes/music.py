"""
音乐生成 API 路由
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
import io
import base64

from app.models.schemas import (
    MusicGenerateRequest,
    MusicResponse,
    MusicStyle,
)
from app.services.github_service import GitHubService
from app.services.commit_analyzer import CommitAnalyzer
from app.services.music_generator import MusicGenerator
from app.services.midi_builder import MidiBuilder
from app.api.deps import get_github_service


router = APIRouter()


@router.post("/generate", response_model=MusicResponse)
async def generate_music(
    request: MusicGenerateRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    根据 GitHub 仓库生成音乐
    
    返回 JSON 格式的音乐数据，供前端 Tone.js 播放
    """
    try:
        # 1. 获取 commits
        owner, repo = github_service.parse_repo_url(request.repo_url)
        commits = await github_service.get_commits(
            owner, repo,
            max_count=request.max_commits
        )
        
        # 2. 分析 commits
        analyzer = CommitAnalyzer()
        analysis = analyzer.analyze(commits)
        
        # 3. 生成音乐数据
        generator = MusicGenerator(
            style=request.style,
            bpm=request.bpm,
            scale=request.scale
        )
        music_data = generator.generate(analysis)
        
        # 4. 生成 MIDI 文件（Base64）
        midi_builder = MidiBuilder()
        midi_bytes = midi_builder.build(music_data)
        midi_base64 = base64.b64encode(midi_bytes).decode('utf-8')
        
        return MusicResponse(
            success=True,
            repo_name=f"{owner}/{repo}",
            style=request.style,
            bpm=request.bpm,
            duration=music_data.total_duration,
            music_data=music_data,
            midi_base64=midi_base64
        )
        
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate music: {str(e)}")


@router.post("/download-midi")
async def download_midi(
    request: MusicGenerateRequest,
    github_service: GitHubService = Depends(get_github_service),
):
    """
    下载 MIDI 文件
    """
    try:
        # 复用 generate 逻辑
        owner, repo = github_service.parse_repo_url(request.repo_url)
        commits = await github_service.get_commits(owner, repo, max_count=request.max_commits)
        
        analyzer = CommitAnalyzer()
        analysis = analyzer.analyze(commits)
        
        generator = MusicGenerator(style=request.style, bpm=request.bpm)
        music_data = generator.generate(analysis)
        
        midi_builder = MidiBuilder()
        midi_bytes = midi_builder.build(music_data)
        
        # 返回文件流
        return StreamingResponse(
            io.BytesIO(midi_bytes),
            media_type="audio/midi",
            headers={
                "Content-Disposition": f"attachment; filename={repo}_rhythm.mid"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/styles")
async def get_available_styles():
    """
    获取可用的音乐风格
    """
    return {
        "styles": [
            {"id": style.value, "name": style.name.title()}
            for style in MusicStyle
        ]
    }