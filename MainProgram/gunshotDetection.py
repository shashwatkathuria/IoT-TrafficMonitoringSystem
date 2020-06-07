# Gunshot detected, take photo of road and light detect

# Importing required libraries
import pyaudio, picamera, datetime
import numpy as np
import matplotlib.pyplot as plt

camera = picamera.PiCamera()

# Offset for starting frequencies (noise) near mic
NOISE_OFFSET = 10

def main():

    # Running the spectrum analyzer
    spectrumAnalyzer = SpectrumAnalyzer()

def analyzeGunShotAndCaptureImages(spectrumArray):
    """Function to analyze gunshot and take pictures from piCamera if a gunshot is detected."""

    # Getting the peak of the spectrumArray
    maxSpec = max(spectrumArray[NOISE_OFFSET : ])
    spectrumArrayCopy = spectrumArray[:]

    # Mapping the array uniformly to relative percentage terms (with max value as 100)
    for i in range(len(spectrumArrayCopy)):
        spectrumArrayCopy[i] = (spectrumArrayCopy[i] / maxSpec) * 100

    # Analyzing gunshot
    # Getting the top of triangle (>= 80 in relative percentage terms)
    topOfTriangle = np.where(spectrumArrayCopy >= 80)[0]
    # Getting the middle of triangle (>=50 and <= 80 in relative percentage terms)
    middleOfTriangle = np.where(np.logical_and(spectrumArrayCopy <= 80, spectrumArrayCopy >= 50))[0]
    # Getting the bottom values (<=50 in relative percentage terms)
    bottomValues = np.where(spectrumArrayCopy <= 50)[0]

    # Initializing the variables required
    topTriangleCount = 0
    middleTriangleCount = 0
    bottomValuesCount = 0

    # Getting count of high spectrum values near 2500Hz
    for spectrumValue in topOfTriangle:
        # Ignoring higher frequencies
        if spectrumValue < 1024:
            if spectrumValue > 200 and spectrumValue < 350:
                topTriangleCount += 1

    # Getting count of middle spectrum values near peak of 2500Hz triangle
    for spectrumValue in middleOfTriangle:
        # Ignoring higher frequencies
        if spectrumValue < 1024:
            if spectrumValue > 100 and spectrumValue < 200:
                middleTriangleCount += 1

    # Getting count of low spectrum values
    for spectrumValue in bottomValues:
        # Ignoring higher frequencies
        if spectrumValue < 1024:
            if spectrumValue < 200 or spectrumValue > 350:
                bottomValuesCount += 1

    # Conditions for gunshot
    if topTriangleCount != 0 and bottomValuesCount < 900:

        nameOfFile = str(datetime.datetime.now()) + '.jpg'

        # Conditions for gunshot
        if middleTriangleCount > 15 and topTriangleCount > 5:
            camera.capture(nameOfFile)
            print("Gunshot detected")
        elif topTriangleCount > 5:
            camera.capture(nameOfFile)
            print("Gunshot possibility")
        elif middleTriangleCount > 20:
            camera.capture(nameOfFile)
            print("Gunshot possibility")
        elif middleTriangleCount > 10 and topTriangleCount >= 2:
            camera.capture(nameOfFile)
            print("Gunshot possibility")

    # Returning relative percentage values to plot
    return spectrumArrayCopy


class SpectrumAnalyzer:

    # Initializing class variable constants
    CHANNELS = 1
    RATE = 44100
    CHUNK = 4096
    N = CHUNK
    START = 0

    def __init__(self):
        """Function to initialize values as required."""

        # Variable to store audio input data
        self.data = []

        # Initializing variables as required
        self.pa = pyaudio.PyAudio()
        self.stream = self.pa.open(format = pyaudio.paFloat32,
            channels = self.CHANNELS,
            rate = self.RATE,
            input = True,
            output = False,
            frames_per_buffer = self.CHUNK)

        # Initializing spectrum graph
        self.initializeSpectrumGraph()

        # Looping through the audio input continuously
        self.loop()

    def initializeSpectrumGraph(self):
        """Function to initialize the pyplot graph."""

        # X axis definition
        self.f = self.RATE * np.arange(self.N/2) / self.N

        # Initializing plot
        self.fig, axis = plt.subplots(1, 1)
        self.linef, = axis.plot(self.f, np.zeros(len(self.f)))

        # Setting axis labels
        axis.set_xlabel("Freq [Hz]")
        axis.set_ylabel("X(f)")

        # Setting axis limits
        axis.set_xlim(20, self.RATE / 2) # Nyquist
        axis.set_ylim(0, 200)
        plt.show(block = False)

    def loop(self):
        """Function to loop the audio recording cycles."""

        try:
            # Looping till the user stops the program
            while True :

                # Getting data from audio stream in required format
                self.data = self.audioInput()
                # Converting the above data to required Fourier Transform values
                self.fastFourierTransform()
                # Plotting values on the graph
                self.plotGraph()

        # Stopping program on Ctrl + C
        except KeyboardInterrupt:
            print("Ending program")

    def audioInput(self):
        """Function to get the audio input data in required format."""

        # Reading audio input data and converting to required format
        audioInputData = self.stream.read(self.CHUNK, exception_on_overflow = False)
        audioInputData = np.fromstring(audioInputData, np.float32)

        # Returning audio input data
        return audioInputData

    def fastFourierTransform(self):
        """Function to get fast fourier transform (absolute values)."""

        # Setting values
        self.X = np.abs(np.fft.rfft(self.data[self.START : self.START + self.N - 1]))

    def plotGraph(self):
        """Function to plot graph."""

        # Getting values mapped to percentage terms (100) and analyzing gunshot
        self.X = analyzeGunShotAndCaptureImages(self.X)

        # Setting y values of spectrum
        self.linef.set_ydata(self.X)

        # analyzeGunShotAndCaptureImages(self.X)

        # Drawing figure and flushing events
        self.fig.canvas.draw()
        self.fig.canvas.flush_events()

# Calling main function
if __name__ == "__main__":
    main()
