#ifndef _TRANSCIPTION_ITEM
#define _TRANSCIPTION_ITEM

#include "globals.h"

#include <memory>

class TranscriptItem {
public:
  typedef std::unique_ptr<TranscriptItem> pointer_t;
  static void bind(pybind11::module &m);

  TranscriptItem(std::string message_in, TranscriptType transcript_type,
                 thread_id_t destination_id = 0);

  std::string source;
  std::string destination;
  std::string message;
  TranscriptType message_type;
  pybind11::object timestamp;

private:
};

#endif // _TRANSCIPTION_ITEM
