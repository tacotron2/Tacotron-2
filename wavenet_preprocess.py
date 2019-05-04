import argparse
import os
from multiprocessing import cpu_count
from os.path import isfile, join, splitext
import tarfile
from datasets import wavenet_preprocessor
from hparams import hparams
from tqdm import tqdm


def preprocess(args, input_dir, out_dir, hparams):
	
	if args.extract:
		extract_data(input_dir,input_dir)
	mel_dir = os.path.join(out_dir, 'mels')
	wav_dir = os.path.join(out_dir, 'audio')
	os.makedirs(mel_dir, exist_ok=True)
	os.makedirs(wav_dir, exist_ok=True)
	metadata = []
	for folder in os.listdir(input_dir):
		if os.path.isdir(folder):
			in_dir = os.path.join(input_dir,folder)
			speaker_id = hparams.speakers.index(folder.split('_')[2])
			metadata+= wavenet_preprocessor.build_from_path(hparams, in_dir, mel_dir, wav_dir,speaker_id, args.n_jobs, tqdm=tqdm)
	write_metadata(metadata, out_dir)

def write_metadata(metadata, out_dir):
	with open(os.path.join(out_dir, 'map.txt'), 'w', encoding='utf-8') as f:
		for m in metadata:
			f.write('|'.join([str(x) for x in m]) + '\n')
	mel_frames = sum([int(m[5]) for m in metadata])
	timesteps = sum([int(m[4]) for m in metadata])
	sr = hparams.sample_rate
	hours = timesteps / sr / 3600
	print('Write {} utterances, {} audio timesteps, ({:.2f} hours)'.format(
		len(metadata), timesteps, hours))
	print('Max mel frames length: {}'.format(max(int(m[5]) for m in metadata)))
	print('Max audio timesteps length: {}'.format(max(m[4] for m in metadata)))

def run_preprocess(args, hparams):
	output_folder = os.path.join(args.base_dir, args.output)

	preprocess(args, args.input_dir, output_folder, hparams)

def main():
	print('initializing preprocessing..')
	parser = argparse.ArgumentParser()
	parser.add_argument('--base_dir', default='')
	parser.add_argument('--extract', default=True)
	parser.add_argument('--hparams', default='',
		help='Hyperparameter overrides as a comma-separated list of name=value pairs')
	parser.add_argument('--input_dir', default='LJSpeech-1.1/wavs')
	parser.add_argument('--output', default='tacotron_output/gta/')
	parser.add_argument('--n_jobs', type=int, default=cpu_count())
	args = parser.parse_args()

	modified_hp = hparams.parse(args.hparams)

	run_preprocess(args, modified_hp)

def extract_data(data_root,extract_path):
	files = [f for f in listdir(data_root) if isfile(join(data_root, f))]
	for file in files:
		print("Extracting:", file)
		tar = tarfile.open(join(data_root, file), "r:bz2")
		tar.extractall(extract_path)
		tar.close()

if __name__ == '__main__':
	main()
