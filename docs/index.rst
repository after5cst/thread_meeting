thread_meeting Documentation
============================

Primitives for cross-Python-thread communication.

A "Meeting" is a concept where one or more Python threads choose to
participate in a queue-based messaging system.

Each thread that participates is known as an Attendee and can do
any of the following:

* Post a message to its own queue
* Pick up messages from its queue
* Request a Baton, which has the right to post to all other Attendee queues.
* Configure itself to be interrupted via an exception when something is
  posted to its queue from another Attendee.

Contents:

.. toctree::
   :maxdepth: 2

   thread_meeting
