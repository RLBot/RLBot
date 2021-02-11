#pragma once

// blocking_reader.h - a class that provides basic support for
// blocking & time-outable single character reads from
// boost::asio::serial_port.
//
// use like this:
//
// 	blocking_reader reader(port, 500);
//
//	char c;
//
//	if (!reader.read_char(c))
//		return false;
//
// Kevin Godden, www.ridgesolutions.ie
// https://www.ridgesolutions.ie/index.php/2012/12/13/boost-c-read-from-serial-port-with-timeout-example/
//

#include <boost/asio.hpp>
#include <boost/bind.hpp>

class SocketReaderWithTimeout
{
    boost::asio::ip::tcp::socket& socket;
    boost::asio::deadline_timer timer;
    bool read_error;

    // Called when an async read completes or has been cancelled
    void read_complete(const boost::system::error_code& error,
                       size_t bytes_transferred) {

        read_error = (error || bytes_transferred == 0);

        // Read has finished, so cancel the
        // timer.
        timer.cancel();
    }

    // Called when the timer's deadline expires.
    void time_out(const boost::system::error_code& error) {

        // Was the timeout was cancelled?
        if (error) {
            // yes
            return;
        }

        // no, we have timed out, so kill
        // the read operation
        // The read callback will be called
        // with an error
        socket.cancel();
    }

public:

    // Constructs a blocking reader, pass in an open serial_port and
    // a timeout in milliseconds.
    SocketReaderWithTimeout(boost::asio::ip::tcp::socket & socket) :
            socket(socket),
            timer(socket.get_io_service()),
            read_error(true) {

    }

    // Reads a character or times out
    // returns false if the read times out
    bool read_data(int num_bytes, int timeout_millis, boost::asio::streambuf* buffer) {

        // After a timeout & cancel it seems we need
        // to do a reset for subsequent reads to work.
        socket.get_io_service().reset();

        boost::asio::async_read(
                socket,
                *buffer,
                boost::asio::transfer_exactly(num_bytes),
                boost::bind(&SocketReaderWithTimeout::read_complete,
                            this,
                            boost::asio::placeholders::error,
                            boost::asio::placeholders::bytes_transferred));


        // Setup a deadline time to implement our timeout.
        timer.expires_from_now(boost::posix_time::milliseconds(timeout_millis));
        timer.async_wait(boost::bind(&SocketReaderWithTimeout::time_out,
                                     this, boost::asio::placeholders::error));

        // This will block until a character is read
        // or until the it is cancelled.
        socket.get_io_service().run();

        return !read_error;
    }
};