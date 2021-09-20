
def determineBestQuality(data):
    best_quality = None
    for video in data:
        if best_quality is None:
            if video["quality"] == "1080p":
                best_quality = "1080p"
            if video["quality"] == "720p":
                best_quality = "720p"
            if video["quality"] == "480p":
                best_quality = "480p"
            if video["quality"] == "360p":
                best_quality = "360p"
            if video["quality"] == "240p":
                best_quality = "240p"
            if video["quality"] == "144p":
                best_quality = "144p"
        if best_quality == "720p":
            if video["quality"] == "1080p":
                best_quality = "1080p"
        if best_quality == "480p":
            if video["quality"] == "1080p":
                best_quality = "1080p"
            if video["quality"] == "720p":
                best_quality = "720p"
        if best_quality == "360p":
            if video["quality"] == "1080p":
                best_quality = "1080p"
            if video["quality"] == "720p":
                best_quality = "720p"
            if video["quality"] == "480p":
                best_quality = "480p"
        if best_quality == "240p":
            if video["quality"] == "1080p":
                best_quality = "1080p"
            if video["quality"] == "720p":
                best_quality = "720p"
            if video["quality"] == "480p":
                best_quality = "480p"
            if video["quality"] == "360p":
                best_quality = "360p"
        if best_quality == "144p":
            if video["quality"] == "1080p":
                best_quality = "1080p"
            if video["quality"] == "720p":
                best_quality = "720p"
            if video["quality"] == "480p":
                best_quality = "480p"
            if video["quality"] == "360p":
                best_quality = "360p"
            if video["quality"] == "240p":
                best_quality = "240p"
    return best_quality

def determineDAVideo(data):
    if len(data) == 1:
        return data[0]["src"]
    else:
        best_quality = determineBestQuality(data)
