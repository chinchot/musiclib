import argparse


def parse_args():
    parser = argparse.ArgumentParser(description='Music catalog')
    parser.add_argument('--path', '-p', type=str, dest='input_path', required=True,
                        default='.', help='The path containing the files')
    parser.add_argument('--album', '-a', type=str, dest='album_name', required=False,
                        help='Name of the album being fix')
    parser.add_argument('--artist', '-t', type=str, dest='artist_name', required=False,
                        help='Name of the artist for the album being fix')
    parser.add_argument('--compilation', '-c', type=bool, dest='album_compilation', default=False,
                        help='Is it an album compilation or single artist')
    parser.add_argument('--disc_split', '-d', type=int, dest='disc_splits', action='append', required=False,
                        help='Number of the songs in each disc, when multiple discs are in the same path')
    parser.add_argument('--ratio', '-r', type=int, dest='match_ratio', default=100,
                        help='Ratio to be applied for fuzzy match track name lookup')
    return parser.parse_args()
