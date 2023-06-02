import serial
import matplotlib.pyplot as plt
from collections import deque
import time
import numpy as np

# Set the Arduino port and baud rate
arduino_port = "COM4"  # Replace with your Arduino port
baud_rate = 115200  # Make sure it matches your Arduino's baud rate

# Create lists to store time and data values
max_data_points = 1000  # Adjust the number of data points as needed
time_values = deque(maxlen=max_data_points)
data_values = deque(maxlen=max_data_points)

# Establish connection with Arduino
arduino = serial.Serial(arduino_port, baud_rate)

# Set interactive mode for the plot
plt.ion()

# Create the time domain plot
fig1, ax1 = plt.subplots()
line1, = ax1.plot([], [])
ax1.set_xlim(0, 10)  # Initial x-axis limits
ax1.set_ylim(0, 1023)  # Adjust the y-axis limits based on your analogRead range
ax1.set_xlabel('Time')
ax1.set_ylabel('Data')
ax1.set_title('Time Domain Graph')
ax1.grid(True)

# Create the frequency domain plot
fig2, ax2 = plt.subplots()
bar_container = ax2.bar([], [], width=1)
ax2.set_xlim(0, 50)  # Adjust the x-axis limits as needed
ax2.set_ylim(0, 500)  # Adjust the y-axis limits based on your data range
ax2.set_xlabel('Frequency')
ax2.set_ylabel('Amplitude')
ax2.set_title('Frequency Domain Graph')
ax2.grid(True)

# Create the spectrogram plot
fig3, ax3 = plt.subplots()
ax3.set_xlabel('Time')
ax3.set_ylabel('Frequency')
ax3.set_title('Spectrogram')
ax3.grid(True)

# Start time for tracking the elapsed time
start_time = time.time()

try:
    while True:
        if arduino.in_waiting > 0:
            try:
                # Read audio data from Arduino
                data = arduino.readline().decode().strip()
                if data:
                    # Add the current time and data value to the deque
                    current_time = time.time() - start_time
                    time_values.append(current_time)
                    data_values.append(int(data))

                    # Remove data points older than the specified time frame
                    while time_values and current_time - time_values[0] > 10:
                        time_values.popleft()
                        data_values.popleft()

                    # Update the time domain plot
                    line1.set_data(time_values, data_values)
                    ax1.relim()

                    # Adjust x-axis limits based on the current maximum time value
                    max_time = max(time_values)
                    ax1.set_xlim(max_time - 10, max_time)

                    ax1.autoscale_view()

                    # Redraw the time domain plot
                    fig1.canvas.draw()
                    fig1.canvas.flush_events()

                    # Perform Fourier transform on the data
                    fft_data = np.fft.fft(data_values)
                    freq = np.fft.fftfreq(len(data_values), 1.0 / len(data_values))

                    # Calculate the amplitude spectrum
                    amplitude = np.abs(fft_data)

                    # Update the frequency domain plot
                    ax2.clear()
                    bar_container = ax2.bar(freq, amplitude, width=1)
                    ax2.set_xlim(0, 50)  # Adjust the x-axis limits as needed
                    ax2.set_ylim(0, 500)  # Adjust the y-axis limits based on your data range
                    ax2.set_xlabel('Frequency')
                    ax2.set_ylabel('Amplitude')
                    ax2.set_title('Frequency Domain Graph')
                    ax2.grid(True)

                    # Redraw the frequency domain plot
                    fig2.canvas.draw()
                    fig2.canvas.flush_events()

                    # Update the spectrogram
                    ax3.specgram(data_values, NFFT=256, Fs=1000)

                    # Redraw the spectrogram
                    fig3.canvas.draw()
                    fig3.canvas.flush_events()

            except UnicodeDecodeError:
                # Handle UnicodeDecodeError
                print("UnicodeDecodeError occurred. Skipping data.")

            except ValueError:
                # Handle ValueError
                print("ValueError occurred. Skipping data.")

except KeyboardInterrupt:
    pass

# Close the serial connection
arduino.close()
