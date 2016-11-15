FROM fedora:24

# Install packages
RUN dnf -y install mock rpm-build vim-enhanced curl man man-pages less

# Add a non-privileged user and add to mock group so it has build privs
RUN useradd -m builder
RUN gpasswd -a builder mock

# Tweak vim config
RUN echo $'colorscheme elflord\n\
noremap <leader>\ :nohlsearch<CR>\n\
set statusline=%F%M%r%h%w\ %y\ [%{&ff}]\ ascii=\%03.3b\ hex=\%02.2B%=%14.(%l,%v%)\ (%p%%)\n\
set laststatus=2' >>/home/builder/.vimrc

# Set up build env
RUN echo "_topdir /home/builder/rpmbuild" >/home/builder/.rpmmacros
RUN mkdir -p /home/builder/{bin,mock} /home/builder/rpmbuild/{BUILD,BUILDROOT,SOURCES,SPECS,SRPMS,RPMS}

# Add some information to login profile
#RUN echo "test -f ~/.aliases && source ~/.aliases" >>~/.bash_profile

# Copy files
COPY motd /etc/motd
COPY aliases /home/builder/
COPY bin/* /home/builder/bin/
COPY rpmbuild/SPECS/* /home/builder/rpmbuild/SPECS/
COPY rpmbuild/SOURCES/* /home/builder/rpmbuild/SOURCES/

# Add aliases to bashrc
RUN cat /home/builder/aliases >>/home/builder/.bashrc
RUN rm /home/builder/aliases

# Fix ownership
USER root
RUN chown -R builder:builder /home/builder

# Download sources
RUN su - builder -c "get-sources"

# Built packages will go here
VOLUME mock

# Back to the builder user and prep for container to be started in interactive mode
USER builder
WORKDIR /home/builder
CMD cat /etc/motd; /bin/bash -l
