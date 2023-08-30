def main():
    parser = argparse.ArgumentParser(description='Calculate voltage, power, and current')
    parser.add_argument('--resistance', type=float, required=False, default=0.1, help='Resistance of the wire')
    parser.add_argument('--length_of_one_side', type=float, required=False, default=1, help='Length of one side of the coil')
    parser.add_argument('--distance_coils', type=float, required=False, default=0.54, help='Distance between coils')
    parser.add_argument('--number_turns', type=float, required=False, default=20.0, help='Number of turns in the coil')
    parser.add_argument('--measured_axis', type=str, required=False, default='z', help='Axis along which measurements are taken')
    parser.add_argument('--number_of_datapoints', type=str, required=False, default=50, help='Number of data points to be collected')
    args = parser.parse_args()


if __name__ == "__main__":
    main()