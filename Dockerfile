FROM fedora:27
EXPOSE 35000
CMD ["run_api.sh"]
ENV \
 THOTH_RESULT_API_INSTALL='/tmp/thoth_result_api_install'

COPY ./ "${THOTH_RESULT_API_INSTALL}"
RUN \
  dnf update -y &&\
  dnf install -y python3-pip &&\
  cd "${THOTH_RESULT_API_INSTALL}" &&\
  pip3 install -r requirements.txt &&\
  cp api_v1.py /usr/local/bin &&\
  cp hack/run_api.sh /usr/local/bin &&\
  cd / &&\
  dnf clean all &&\
  rm -rf "${THOTH_RESULT_API_INSTALL}"
