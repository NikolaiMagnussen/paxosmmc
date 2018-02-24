#!/usr/bin/env python3
import subprocess
import re
import numpy as np
import matplotlib.pyplot as plot


def run_experiment(max_conc, trials):
    print(f"Running experiment with {trials} trials and from 1 to {max_conc} "
          "concurrency")
    to_match = re.compile(r""".*completed (\d+).*in (.*)s.*""")
    reqs_per_sec = []
    for i in range(1, max_conc + 1):
        print(f"\nRunning trials for concurrency level {i}")
        for j in range(trials):
            paxos = subprocess.Popen(["python3", "env.py", f"-c={i}"],
                                     stdout=subprocess.PIPE)
            try:
                paxos.wait(10)
                out, _ = paxos.communicate()
                match = to_match.match(out.decode())
                reqs_per_sec.append(int(match.group(1))/float(match.group(2)))
            except subprocess.TimeoutExpired:
                paxos.kill()
                reqs_per_sec.append(reqs_per_sec[-1])
                print("Timed out: duplicated last value instead")
            print(f"\tTrial {j} completed for {i} concurrent clients")
        print(f"Completed trials for concurrency level {i}")

    print(f"Got {len(reqs_per_sec)} samples: {reqs_per_sec}")

    return reqs_per_sec


def calculate_statistics(data):
    # Remove the two most extreme values from the samples, given enough samples
    if data.shape[1] >= 5:
        data.sort(axis=1)
        data = np.delete(data, [0, data.shape[1]-1], 1)

    # Calculate statistics based off that data
    stds = data.std(axis=1)
    means = data.mean(axis=1)

    return means, stds


def plot_statistics(means, stds):
    print("Plotting the statistics!")

    # Set XKCD mode graph
    plot.xkcd()

    # Plot data
    xs = np.linspace(1, len(means), num=len(means))
    plot.errorbar(xs, means, yerr=stds)
    plot.xticks(xs)
    plot.title("Paxos throughput as a function of concurrent clients")
    plot.xlabel("Number of concurrent clients")
    plot.ylabel("Number of requests per second")
    plot.show()


def main():
    max_conc = 20
    trials = 50

    requests_per_second = np.array(run_experiment(max_conc, trials))
    data = requests_per_second.reshape(max_conc, trials)

    means, stds = calculate_statistics(data)
    plot_statistics(means, stds)


if __name__ == "__main__":
    main()
