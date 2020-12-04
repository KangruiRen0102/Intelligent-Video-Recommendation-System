from train_utility import train_model, report_model
import argparse
import os

parser = argparse.ArgumentParser()
# parser.add_argument('--data_folder', metavar='N', type=str, default = os.path.join(my_path, '../dataset/final_csv/')
#                     help='dataset folder')
parser.add_argument('--val_ratio', metavar='N', type=float, default=0.1,
                    help="validation ratio")
parser.add_argument('--embeddeding_size', metavar='N', type=int, default=50,
                    help="embeddeding size for item and user")
parser.add_argument('--batch_size', metavar='N', type=int, default=256,
                    help="batch size")
parser.add_argument('--epochs', metavar='N', type=int, default=5,
                    help="training epochs")
args = parser.parse_args()


if __name__ == '__main__':
    my_path = os.path.abspath(os.path.dirname(__file__))
    model_path = os.path.join(my_path, '../checkpoint/model/')
    train_model(model_path, args.val_ratio, args.embeddeding_size, args.batch_size, args.epochs)
