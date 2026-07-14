# PySpark Basics

## Setup

PySpark requires a Java runtime and GNU coreutils to run on macOS.

### 1. Java 17

PySpark 4.x requires Java 17 (class file version 61.0). Java 11 or below will throw an `UnsupportedClassVersionError`.

Install via Homebrew and register with macOS:

```sh
brew install openjdk@17
sudo ln -sfn /opt/homebrew/opt/openjdk@17/libexec/openjdk.jdk /Library/Java/JavaVirtualMachines/openjdk-17.jdk
```

Add to `~/.zshrc` under the `# JAVA` section:

```sh
export JAVA_HOME=/Library/Java/JavaVirtualMachines/openjdk-17.jdk/Contents/Home
export PATH=$JAVA_HOME/bin:$PATH
```

Verify:

```sh
java -version  # should show openjdk 17
```

### 2. GNU coreutils

PySpark's `spark-class` shell script uses `head -n -1` (strip last line), which macOS's BSD `head` does not support. GNU coreutils provides a compatible replacement.

Install via Homebrew:

```sh
brew install coreutils
```

Add to `~/.zshrc` under the `# PYTHON` section:

```sh
export PATH="/opt/homebrew/opt/coreutils/libexec/gnubin:$PATH"
```

### 3. Python dependencies

Install PySpark and other dependencies into a virtual environment:

```sh
uv pip install -r requirements.txt --system-certs
```

> `--system-certs` is required in corporate/VPN environments where a custom CA certificate is in use.

### 4. Apply shell config

After editing `~/.zshrc`, open a new terminal (or run `source ~/.zshrc`) to pick up the changes before running the script.

## Running

```sh
cd python_sandbox/pyspark_basics
python main.py
```

