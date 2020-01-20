#ifndef TAKE_H
#define TAKE_H
#include <memory>
#include <pybind11/pybind11.h>
#include "globals.h"

class Take
{
public:
    typedef std::shared_ptr<Take> pointer_t;
    typedef std::shared_ptr<MessageStatus> status_t;

    static void bind(pybind11::module&);
    Take(std::string name_in, pybind11::object payload_in, 
         bool transcribe_status=false)
        : name(name_in), payload(payload_in),
          status(std::make_shared<MessageStatus>(MessageStatus::pending)),
          m_transcribe(transcribe_status)
    {}
    // We don't allow copying OR moving this object.
    // So by rule of 5, we need to specify all five.
    ~Take() { set_status(MessageStatus::acknowledged, false); }
    Take(const Take&) = delete;
    Take& operator=(const Take& other) = delete;
    Take(Take&&) = delete;
    Take& operator=(Take&&) = delete;

    // Methods for Python access
    void acknowledge() { set_status(MessageStatus::acknowledged); }
    void protest() { set_status(MessageStatus::protested); }

    std::string name;
    pybind11::object payload;
    status_t status;

private:
    void set_status(MessageStatus new_status, bool throw_on_error = true);
    bool m_transcribe;
};

#endif // TAKE_H
