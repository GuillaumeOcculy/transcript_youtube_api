from flask import Flask, request, jsonify
from youtube_transcript_api import YouTubeTranscriptApi, TranscriptsDisabled, NoTranscriptFound, VideoUnavailable

app = Flask(__name__)

def get_transcript_auto(video_id):
    languages_to_try = [['en'], ['fr'], ['fr', 'fr-auto']]
    for languages in languages_to_try:
        try:
            return YouTubeTranscriptApi.get_transcript(video_id, languages=languages)
        except NoTranscriptFound:
            continue
        except TranscriptsDisabled:
            return {'error': 'Les transcriptions sont désactivées pour cette vidéo.'}
        except VideoUnavailable:
            return {'error': 'Vidéo YouTube non disponible ou supprimée.'}
        except Exception as e:
            return {'error': f'Erreur inconnue : {str(e)}'}
    return {'error': 'Aucune transcription disponible dans les langues supportées.'}

@app.route("/transcript", methods=["GET"])
def transcript_endpoint():
    video_id = request.args.get("video_id")
    if not video_id:
        return jsonify({"error": "Paramètre 'video_id' requis"}), 400
    result = get_transcript_auto(video_id)
    if isinstance(result, dict) and "error" in result:
        return jsonify(result), 400
    full_text = " ".join([entry["text"] for entry in result])
    segments = [{"start": round(e["start"], 2), "duration": round(e["duration"], 2), "text": e["text"]} for e in result]
    return jsonify({"video_id": video_id, "transcript": full_text, "segments": segments})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=10000)
