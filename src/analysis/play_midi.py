import pygame
import sys

def play_music(midi_file):
    """Stream music_file in a blocking manner"""
    clock = pygame.time.Clock()
    try:
        pygame.mixer.music.load(midi_file)
        print(f"Music file {midi_file} loaded!")
    except pygame.error:
        print(f"File {midi_file} not found! ({pygame.get_error()})")
        return
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        # check if playback has finished
        clock.tick(30)

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python play_midi.py <midi_file>")
        sys.exit(1)

    midi_file = sys.argv[1]
    
    # init pygame
    pygame.init()
    pygame.mixer.init()
    
    play_music(midi_file)
