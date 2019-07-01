FROM ubuntu:rolling

# install ubuntu packages from file
COPY ubuntu-dependencies.txt /tmp/
RUN apt-get update && xargs -a /tmp/ubuntu-dependencies.txt apt-get install -y

# python2 node2vec
RUN git clone https://github.com/aditya-grover/node2vec.git
RUN python -m pip install -r /node2vec/requirements.txt
# add scala build tool (needed for building joern)
RUN echo "deb https://dl.bintray.com/sbt/debian /" | tee -a /etc/apt/sources.list.d/sbt.list
RUN apt-key adv --keyserver hkp://keyserver.ubuntu.com:80 --recv 2EE0EA64E40A89B84B2DF73499E82A75642AC823
RUN apt-get update && apt-get install -y sbt

# python clang bindings
RUN wget --output-document=/tmp/clang-source.tar.xz \
    "http://releases.llvm.org/$(llvm-config --version)/cfe-$(llvm-config --version).src.tar.xz"
RUN tar --extract --xz --file="/tmp/clang-source.tar.xz"
RUN mv "/cfe-$(llvm-config --version).src" "/clang-source"

ENV PYTHONPATH "${PYTHONPATH}:/clang-source/bindings/python"

# snap-python (for node2vec)
RUN cd /tmp && wget "http://snap.stanford.edu/snappy/release/beta/snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
RUN cd /tmp && tar --extract --gz --file="snap-5.0.9-64-3.0-centos6.5-x64-py3.6.tar.gz"
RUN cd /tmp/snap-5.0.0-64-3.0-centos6.5-x64-py3.6 && python3 setup.py install

# graph2vec
# can be run via python3 /graph2vec/src/graph2vec.py <args>
RUN git clone https://github.com/benedekrozemberczki/graph2vec.git

# joern
RUN git clone https://github.com/ShiftLeftSecurity/joern.git /joern
RUN cd joern && sbt stage

# Prolog and ILP
RUN git clone --depth 1 https://github.com/vscosta/yap-6.3 /yap
RUN mkdir /yap/build && cd /yap/build && cmake ../ && make && make install

RUN mkdir /aleph && wget --output-document=/aleph/aleph.pl \
         "http://www.comlab.ox.ac.uk/oucl/research/areas/machlearn/Aleph/aleph.pl"
RUN git clone --depth 1 https://github.com/metagol/metagol.git /metagol

# Add metagol to swi-prolog path
COPY .swiplrc /root/.swiplrc

# Python dependencies. These are most likely to change, so go near the bottom.
RUN python -m pip install --upgrade pip
COPY requirements-py2.txt /tmp/
RUN python -m pip install --requirement /tmp/requirements-py2.txt

RUN python3 -m pip install --upgrade pip
COPY requirements-py3.txt /tmp/
RUN python3 -m pip install --requirement /tmp/requirements-py3.txt

# Add python 2 as a kernel for jupyter
RUN python -m pip install ipykernel
RUN python -m ipykernel install

# Run for a jupyter notebook by default
WORKDIR "/project"
EXPOSE 8888
CMD ["jupyter", "notebook", "--allow-root", "--ip", "0.0.0.0", "--no-browser"]