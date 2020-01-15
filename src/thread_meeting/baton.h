#ifndef _BATON_H
#define _BATON_H

#include "globals.h"
#include "pybind11/pybind11.h"

#include <memory>

class Baton
{
public:
    typedef std::shared_ptr<Baton> pointer_t;
    static void bind(pybind11::module& m);

    Baton() : m_owner_thread_id(get_python_thread_id()) {}

    long get_owner_thead_id() const { return m_owner_thread_id; }
    void invalidate() { m_owner_thread_id = INVALID_THREAD_ID; }

    bool valid() const { return m_owner_thread_id != INVALID_THREAD_ID; }
private:
    long m_owner_thread_id;
    const long INVALID_THREAD_ID = 0;
};

#endif // _BATON_H
