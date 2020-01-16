#ifndef TAKE_H
#define TAKE_H
#include <memory>
#include <pybind11/pybind11.h>

class Take
{
public:
    enum class Status { pending, acknowledged, protested };
    typedef std::shared_ptr<Take> pointer_t;
    typedef std::shared_ptr<Status> status_t;

    static void bind(pybind11::module&);
    Take(std::string name_in, pybind11::object payload_in)
        : name(name_in), payload(payload_in),
          status(std::make_shared<Status>(Status::pending))
    {}
    // We don't allow copying OR moving this object.
    // So by rule of 5, we need to specify all five.
    ~Take() { set_status(Status::acknowledged, false); }
    Take(const Take&) = delete;
    Take& operator=(const Take& other) = delete;
    Take(Take&&) = delete;
    Take& operator=(Take&&) = delete;

    // Methods for Python access
    void acknowledge() { set_status(Status::acknowledged); }
    void protest() { set_status(Status::protested); }

    std::string name;
    pybind11::object payload;
    status_t status;

private:
    void set_status(Status new_status, bool throw_on_error = true)
    {
        assert(new_status != Status::pending);
        if (*status == Status::pending)
        {
            *status = new_status;
        }
        else if (*status == new_status)
        {
            // Do nothing: setting a status to itself is a NOOP.
        }
        else if (throw_on_error)
        {
            std::string msg = "Status of Take('" + name + "') already set";
            throw std::invalid_argument(msg);
        }
    }
};

#endif // TAKE_H
