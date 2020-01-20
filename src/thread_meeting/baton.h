#ifndef _BATON_H
#define _BATON_H

#include "globals.h"
#include "keep.h"
#include "pybind11/pybind11.h"

#include <memory>

class Baton
{
public:
    typedef std::shared_ptr<Baton> pointer_t;
    static void bind(pybind11::module& m);

    Baton() : m_owner_thread_id(PyThread_get_thread_ident()) {}

    thread_id_t get_owner_thead_id() const { return m_owner_thread_id; }
    void invalidate() { m_owner_thread_id = INVALID_THREAD_ID; }

    std::unique_ptr<Keep> post(
            std::string name, pybind11::object payload);

    bool valid() const { return m_owner_thread_id != INVALID_THREAD_ID; }
private:
    thread_id_t m_owner_thread_id;
    const thread_id_t INVALID_THREAD_ID = 0;
};

#endif // _BATON_H
