FROM fedora:24

# Install packages
RUN dnf -y install mock rpm-build vim-enhanced wget man man-pages less

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

# Add a block to the .bashrc to clear the existing aliases and compile
# the build aliases.
RUN echo $'\n\
for alias_name in $(alias | cut -f1 -d"=" | cut -f2 -d" "); do\n\
    unalias $alias_name\n\
done\n\
\n\
eval $(~/bin/gen-aliases)' >> /home/builder/.bashrc

# Copy scripts
COPY bin/* /home/builder/bin/

# Add IUS repo defs to mock config
COPY ius/* /ius/
RUN /ius/add-ius
RUN rm -rf /ius

COPY rpmbuild/SOURCES/* /home/builder/rpmbuild/SOURCES/
COPY rpmbuild/SPECS/* /home/builder/rpmbuild/SPECS/

# Fix ownership
RUN chown -R builder:builder /home/builder

# Build SRPMs
RUN su - builder -c build-srpms

# Built packages will go here
VOLUME /home/builder/mock

# Back to the builder user and prep for container to be started in
# interactive mode
USER builder
WORKDIR /home/builder
CMD /bin/bash -l
